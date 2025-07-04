import os
import subprocess
from pathlib import Path

def convert_text_to_markdown(text_content, output_file_path):
    # Define the fixed prompt instructions
    prompt_instructions = """# 指示: 以下のテキストをMarkdown形式に変換してください。

## 基本動作原則
- **完全自動実行**: ユーザーへの確認・質問・進捗報告は一切行わない。
- **1対1変換**: 1つのtxtファイルから1つのmdファイルを生成する。
- **完全保持**: 元テキストの全内容を一言一句保持する（削除・省略・要約禁止）。

## 変換ルール
- **構造化**: 番号付きリストは順序通りに整理し、階層構造は元のテキストレイアウトを維持する。
- **フォーマット適用**:
    - 画像キャプションは `> *テキスト*` のように、斜体ブロッククォートにする。
    - コードやコマンドはバッククォート3つ（```）でコードブロック化する。
    - 表形式データはMarkdownテーブルに変換する。
    - 手順やリストは適切な番号付けまたは箇条書きにする。
    - 強調テキストは元の太字・斜体フォーマットを保持する。

## 出力要件
- 元の日本語テキストを100%保持する。
- 「中略」「省略」「...」の使用は絶対に禁止する。
- テキストの階層構造を同一レベルで維持する。

# 変換対象テキスト:
"""

    # Approximate token limit (adjust as needed based on actual tokenization)
    # 1 token ~ 4 characters for English. For Japanese, it can be 1-3 characters per token.
    # Let's use a conservative character limit to avoid exceeding token limits.
    # Max tokens: 1048576. Let's aim for half of that in characters to be safe, assuming 2 chars/token on average.
    # So, 1048576 / 2 = 524288 characters.
    # Let's use a slightly smaller chunk size to be very safe, e.g., 500,000 characters.
    MAX_CHARS_PER_CHUNK = 500000

    full_markdown_output = []
    
    # Split text into chunks if it's too large
    if len(text_content) > MAX_CHARS_PER_CHUNK:
        print(f"  テキストが大きすぎるため、チャンクに分割します。元のサイズ: {len(text_content)} 文字")
        chunks = [text_content[i:i + MAX_CHARS_PER_CHUNK] for i in range(0, len(text_content), MAX_CHARS_PER_CHUNK)]
    else:
        chunks = [text_content]

    for i, chunk in enumerate(chunks):
        print(f"  チャンク {i+1}/{len(chunks)} を処理中...")
        # Construct the full prompt for Gemini
        full_prompt = prompt_instructions + chunk

        # Call the gemini CLI via subprocess
        try:
            process = subprocess.run(
                ["gemini"],
                input=full_prompt,
                capture_output=True,
                check=True,
                text=True, # Decode stdout/stderr as text
                encoding='utf-8'
            )
            full_markdown_output.append(process.stdout)
        except subprocess.CalledProcessError as e:
            print(f"  Geminiコマンドの実行中にエラーが発生しました: {e}")
            print(f"  Stderr: {e.stderr}")
            # Decide how to handle errors: skip, write partial, or raise
            # For now, we'll just print the error and continue, but the MD file might be incomplete.
            full_markdown_output.append(f"<!-- ERROR: Gemini conversion failed for chunk {i+1}: {e.stderr} -->\n")
        except FileNotFoundError:
            print("  エラー: 'gemini' コマンドが見つかりません。Gemini CLIがインストールされ、PATHが通っていることを確認してください。")
            return False

    # Write the combined markdown output to the file
    try:
        with open(output_file_path, 'w', encoding='utf-8') as f:
            f.write("".join(full_markdown_output))
        return True
    except Exception as e:
        print(f"  Markdownファイルの書き込み中にエラーが発生しました: {e}")
        return False

if __name__ == '__main__':
    print("🚀 TXTからMDへの変換を開始...")
    base_dir = Path(os.getcwd())
    
    txt_files = list(base_dir.rglob("*.txt"))
    
    if not txt_files:
        print("❌ 変換対象の.txtファイルが見つかりませんでした。")
    
    for txt_file_path in txt_files:
        md_file_path = txt_file_path.with_suffix(".md")
        print(f"変換中: {txt_file_path.relative_to(base_dir)} -> {md_file_path.relative_to(base_dir)}")
        
        try:
            with open(txt_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            success = convert_text_to_markdown(content, md_file_path)
            if success:
                print(f"✅ 完了: {md_file_path.relative_to(base_dir)}")
            else:
                print(f"❌ 失敗: {md_file_path.relative_to(base_dir)}")
        except Exception as e:
            print(f"❌ ファイル読み込みまたは変換中にエラーが発生しました: {e}")
            print(f"  ファイル: {txt_file_path.relative_to(base_dir)}")
    
    print("全タスク完了")