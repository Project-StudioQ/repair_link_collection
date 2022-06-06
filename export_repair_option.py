# ----------------------------------------------------------------------------------------------------
# subprocessからRepair Link Collection設定ファイルの出力用
# ----------------------------------------------------------------------------------------------------

import bpy
import sys


def main():
    try:
        bpy.ops.qcommon.export_repair_option()
    except Exception as e:
        print(e)
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
