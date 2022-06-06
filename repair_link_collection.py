import bpy
import os
import tempfile
import subprocess
import json
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, CollectionProperty, PointerProperty, IntProperty

# ----------------------------------------------------------------------------------------------------
# 定数
# ----------------------------------------------------------------------------------------------------

TEMP_FILE_PATH = os.path.join(tempfile.gettempdir(), "repair_link_collection.json")

# ----------------------------------------------------------------------------------------------------
# Property Group
# ----------------------------------------------------------------------------------------------------


class QCOMMON_SAVE_repair_link_collection_item(bpy.types.PropertyGroup):
    text: StringProperty()


class QCOMMON_SAVE_repair_link_collection(bpy.types.PropertyGroup):
    ignore_targets: CollectionProperty(type=QCOMMON_SAVE_repair_link_collection_item)


# ----------------------------------------------------------------------------------------------------
# Operator
# ----------------------------------------------------------------------------------------------------


class QCOMMON_OT_repair_link_collection(bpy.types.Operator, ImportHelper):
    """リンクしたコレクションの修復"""

    bl_idname = "qcommon.repair_link_collection"
    bl_label = "Select File"

    filter_glob: StringProperty(
        default="*.blend",
        options={"HIDDEN"},
    )

    def invoke(self, context, event):
        if len(context.selected_ids) > 1:
            self.report({"ERROR"}, "Please select only one library.")
            return {"CANCELLED"}

        # 別のLibraryからリンクされているものは無視
        item = context.selected_ids[0]
        if item.parent != None:
            self.report({"ERROR"}, f"Library referenced from\n [{item.parent.name}].")
            return {"CANCELLED"}

        # ImportHelperからのファイル指定を呼び出す
        return super().invoke(context, event)

    def execute(self, context):
        if not os.path.isfile(self.filepath):
            self.report({"ERROR"}, f"[{self.filepath}] is not found.")
            return {"CANCELLED"}
        if self.filepath == bpy.data.filepath:
            self.report(
                {"ERROR"},
                f"[{self.filepath}] is current scene.\nSelect the scene to be repaired",
            )
            return {"CANCELLED"}

        item = context.selected_ids[0]

        # Libraryのパスを置き換え
        item.filepath = self.filepath
        item.reload()

        collections = self._get_repair_target_collections(item)
        # 対象コレクションが無いものは無視
        if len(collections) <= 0:
            self.report(
                {"ERROR"},
                "Target collection is not found.\nMay have already been updated.",
            )
            return {"CANCELLED"}

        data = _load_repair_option(item.filepath)
        repair_name = self._get_repair_collection_name(data)
        if repair_name == None:
            self.report({"ERROR"}, f"Failed to read collection name in [{item.name}].")
            return {"CANCELLED"}

        self._repair_link_collection(collections, repair_name)
        item.reload()

        return {"FINISHED"}

    def _get_repair_collection_name(self, data):
        """修復するコレクション名を取得

        Args:
            data (Dictionary): 修復設定データ

        Returns:
            str: 修復するコレクション名
        """
        props = bpy.context.scene.repair_link_collection

        collections = data["collections"]
        for c in collections:
            target = next(filter(lambda t: t.text not in c, props.ignore_targets), None)
            if target != None:
                return c

        return None

    def _get_repair_target_collections(self, library):
        """修復対象のコレクションリストを取得

        Args:
            library (bpy.types.Library): 対象ライブラリ

        Returns:
            bpy.types.Collection[]: 修復対象のコレクションリスト
        """
        collections = []

        for c in bpy.data.collections:
            if c.library == None:
                continue
            if c.library.filepath != library.filepath:
                continue
            # TODO 壊れていないコレクションは除外するように
            # 壊れているコレクションの取得方法が不明

            collections.append(c)

        return collections

    def _repair_link_collection(self, collections, repair_name):
        """リンクコレクションの修復

        Args:
            collections (bpy.types.Collections): 対象コレクションリスト
            repair_name (str): 修復するコレクション名
        """
        for c in collections:
            c.name = repair_name
            self._rename_link_parent(c)

    def _rename_link_parent(self, collection):
        """リンクされているコレクションの親オブジェクト名をリネーム

        Args:
            collection (bpy.types.Collection): 対象コレクション
        """
        for obj in bpy.data.objects:
            if not obj.instance_collection is collection:
                continue

            obj.name = collection.name


class QCOMMON_OT_export_repair_option(bpy.types.Operator):
    """修復設定の書き出し"""

    bl_idname = "qcommon.export_repair_option"
    bl_label = ""

    def execute(self, context):
        try:
            data = {}
            data["collections"] = [
                c.name for c in bpy.context.scene.collection.children
            ]
            with open(TEMP_FILE_PATH, "w") as f:
                json.dump(data, f)
        except:
            self.report({"ERROR"}, f"Export Failed : {TEMP_FILE_PATH}")
            return {"CANCELLED"}

        self.report({"INFO"}, f"Export Success : {TEMP_FILE_PATH}")
        return {"FINISHED"}


class QCOMMON_OT_repair_link_collection_add_ignore_targets(bpy.types.Operator):
    """除外対象を追加"""

    bl_idname = "qcommon.repair_link_collection_add_ignore_targets"
    bl_label = ""

    def execute(self, context):
        props = context.scene.repair_link_collection
        props.ignore_targets.add()
        return {"FINISHED"}


class QCOMMON_OT_repair_link_collection_remove_ignore_targets(bpy.types.Operator):
    """除外対象を削除"""

    bl_idname = "qcommon.repair_link_collection_remove_ignore_targets"
    bl_label = ""

    index: IntProperty()

    def execute(self, context):
        props = context.scene.repair_link_collection
        props.ignore_targets.remove(self.index)
        return {"FINISHED"}


# ----------------------------------------------------------------------------------------------------
# Panel
# ----------------------------------------------------------------------------------------------------


class QCOMMON_PT_repair_link_collection(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_category = "Q_COMMON"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}
    bl_label = "Repair Link Collection"

    def draw(self, context):
        props = context.scene.repair_link_collection

        layout = self.layout

        col = layout.box().column()
        row = col.row()
        row.label(text="Ignore Texts:")
        row.operator(
            QCOMMON_OT_repair_link_collection_add_ignore_targets.bl_idname,
            text="",
            icon="ADD",
        )
        col2 = col.box().column()
        if len(props.ignore_targets) <= 0:
            col2.label(text="「+」 to add.", icon="INFO")
        else:
            for index, val in enumerate(props.ignore_targets):
                row = col2.row(align=True)
                if val.text == "":
                    row.alert = True
                row.prop(val, "text", text=f"[{index}]")
                op = row.operator(
                    QCOMMON_OT_repair_link_collection_remove_ignore_targets.bl_idname,
                    text="",
                    icon="X",
                )
                op.index = index


# ----------------------------------------------------------------------------------------------------
# Private Functions
# ----------------------------------------------------------------------------------------------------

# -- Check --


def _is_show_repair():
    """修復を表示するか？

    Returns:
        bool: True = 表示する, False = しない
    """
    for item in bpy.context.selected_ids:
        if item.bl_rna.name == "Library":
            return True

    return False


# -- Get --


def _load_repair_option(load_path):
    """修復設定を取得

    Args:
        load_path (str): 読み込みパス

    Returns:
        Dictionary: 修復設定
    """
    # 前のファイルを読み込まないように念のため削除
    if os.path.isfile(TEMP_FILE_PATH):
        os.remove(TEMP_FILE_PATH)

    # 元ファイルから設定を%temp%に出力
    script_path = os.path.join(os.path.dirname(__file__), "export_repair_option.py")
    result = subprocess.run([bpy.app.binary_path, "-b", load_path, "-P", script_path])
    if result.returncode != 0:
        print("Crash Blender when save Repair Link Collection to temporary directory.")
        return None

    try:
        with open(TEMP_FILE_PATH, "r") as f:
            json_data = json.load(f)
    except Exception as e:
        print("Can't load Repair Link Collection from {load_path}")
        return None

    return json_data


# -- UI --


def _draw_menu(self, context):
    """メニューの描画"""
    if not _is_show_repair():
        return

    layout = self.layout
    layout.separator()
    layout.operator(
        QCOMMON_OT_repair_link_collection.bl_idname, text="Repair Link Collection"
    )


# ----------------------------------------------------------------------------------------------------
# Register & Unregister
# ----------------------------------------------------------------------------------------------------

_classes = (
    QCOMMON_SAVE_repair_link_collection_item,
    QCOMMON_SAVE_repair_link_collection,
    QCOMMON_OT_repair_link_collection_add_ignore_targets,
    QCOMMON_OT_repair_link_collection_remove_ignore_targets,
    QCOMMON_OT_repair_link_collection,
    QCOMMON_OT_export_repair_option,
    QCOMMON_PT_repair_link_collection,
)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.repair_link_collection = PointerProperty(
        type=QCOMMON_SAVE_repair_link_collection
    )
    bpy.types.OUTLINER_MT_context_menu.append(_draw_menu)


def unregister():
    del bpy.types.Scene.repair_link_collection
    bpy.types.OUTLINER_MT_context_menu.remove(_draw_menu)

    for cls in _classes:
        bpy.utils.unregister_class(cls)
