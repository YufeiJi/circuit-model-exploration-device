set -e
PY="C:/Users/Yufei Ji/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe"
PLUG="C:/Users/Yufei Ji/.workbuddy-ai/plugins/cache/workbuddy-builtin/tencent-docx/5.7.6-wb.40488862.g3e43260f.had9031c93ded"
cd "D:\Agent\project\电路模型探究装置\文档"
"$PY" build_report.py
cd "$PLUG/skills/html-to-docx/scripts"
"$PY" -m html_to_docx convert "D:\Agent\project\电路模型探究装置\文档/pipeline/stage2/formatted-电路模型探究装置设计报告.html" -o "D:\Agent\project\电路模型探究装置\文档/电路模型探究装置-设计报告.docx"
cd "D:\Agent\project\电路模型探究装置\文档"
"$PY" fix_docx.py "D:\Agent\project\电路模型探究装置\文档/电路模型探究装置-设计报告.docx"
