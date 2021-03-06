# Tools:Q Repair Link Collection

[English](README.en.md)

## 概要
View 3D & Outliner / All Mode

Repair Link Collection は名称が変わったCollectionのリンクを修復するアドオンです。<br>

【修正対象】
* Scene Collection直下のCollection
  * IgnoreTextsの対象を除いて、最初に検知されたものがリンクされます

## UI
![image](https://user-images.githubusercontent.com/1855970/172103134-91b7ab02-0d14-4a51-b9c6-c753f2f58b4b.png)
![image](https://user-images.githubusercontent.com/1855970/172103277-3d071171-0ac0-42bc-bf72-8d4cedf6ccd2.png)

* Ignore Texts
  * 除外対象のコレクションに含まれるテキスト
  * 例：「charA_tmp」を除きたい場合は「_tmp」

## 動画
[![YouTubeで見る](https://img.youtube.com/vi/j5BJpl0iSjs/0.jpg)](https://www.youtube.com/watch?v=j5BJpl0iSjs)

## インストール
Project Studio Qが公開している [Tools:Q](https://github.com/Project-StudioQ/toolsq_common) よりインストールしてください。

## Q&A

* SceneCollection直下以外のコレクションにリンクしていた場合はどうする？
  * 現在はSceneCollection直下以外は対応していません
  * 理由：外部から対象コレクションの指定が難しいため

## ライセンス
このBlenderアドオンは GNU Public License v2 です。
