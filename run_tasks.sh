#!/bin/bash

# --- タスク1: Pythonスクリプトの実行 ---
echo "Pythonスクリプトを実行します..."
python3 local_converter.py
echo "Pythonスクリプトの実行が完了しました。"

echo "----------------------------------------"
echo "TXTからMDへの変換を開始します..."

# --- タスク2: PythonスクリプトでTXTファイルをMDファイルに変換 ---
python3 markdown_converter.py

# --- 完了報告 ---
echo "全タスク完了"