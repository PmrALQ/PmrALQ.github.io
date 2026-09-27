# -*- coding: utf-8 -*-
"""
P0-2 修复脚本 v2:只处理 BlogCard.vue 与 ProjectCard.vue 的
「formatDate 迁移说明」注释块。

修复项(每项独立判断,满足则执行,否则跳过并打印原因):
  [修复1] 重复的注释头: 检测 A1/A2/A1/A2 模式(A1 含「原 formatDate 函数已抽离至」)
          -> 删除第 3、4 行(第二次重复的两行)
  [修复2] 结尾多余的 '*/': 在注释块内检测连续两个独立 '*/' 行
          -> 删除第二个

幂等:重复运行不会再产生变更。
用法:
  python .tmp/fix_p02_block.py             # dry-run
  python .tmp/fix_p02_block.py --apply     # 写入
"""
import sys
from pathlib import Path

ROOT = Path(r"D:/self_website")

KEY = "原 formatDate 函数已抽离至"
KEY2 = "此处保留原始实现供"  # 第二行前缀(兼容"回溯/撤回"等用词)


def has_key(line: str) -> bool:
    return KEY in line


def repair_block(lines: list[str]) -> tuple[list[str], list[str]]:
    """返回 (修改后的行列表, 动作描述列表)。没有修改时行列表不变。"""
    actions: list[str] = []

    key_rows = [i for i, ln in enumerate(lines) if has_key(ln)]
    if not key_rows:
        return lines, actions

    i = key_rows[0]

    # [修复1] 重复头检测: 需要 i+3 < len, 且 行(i+2) == 行(i) 且 行(i+3) == 行(i+1),
    #        且行(i+1) 包含说明第二行前缀 KEY2
    if (
        i + 3 < len(lines)
        and lines[i].strip() == lines[i + 2].strip()
        and lines[i + 1].strip() == lines[i + 3].strip()
        and KEY2 in lines[i + 1]
    ):
        actions.append(
            f"修复1: 删除重复注释头 行{i+3}『{lines[i+2].strip()}』与 行{i+4}『{lines[i+3].strip()}』"
        )
        del lines[i + 3]
        del lines[i + 2]

    # [修复2] 末尾多余的 '*/': 从 KEY 行之后开始, 找连续两个独立 '*/' 行(允许中间空行)
    key_rows = [x for x in range(len(lines)) if has_key(lines[x])]
    if not key_rows:
        return lines, actions
    start = key_rows[0]
    prev_was_star = False
    second_star_row = None
    for j in range(start + 1, len(lines)):
        s = lines[j].strip()
        if s == "":
            continue
        if s == "*/":
            if prev_was_star:
                second_star_row = j
                break
            prev_was_star = True
        else:
            prev_was_star = False
    if second_star_row is not None:
        actions.append(f"修复2: 删除多余 '*/' 行{second_star_row + 1}")
        del lines[second_star_row]

    return lines, actions


def main() -> None:
    apply = "--apply" in sys.argv
    print("== dry-run(未写入任何文件)==" if not apply else "== 应用模式 (--apply) ==")
    print()

    changed_any = False
    for name in ("components/BlogCard.vue", "components/ProjectCard.vue"):
        p = ROOT / name
        if not p.exists():
            print(f"[缺失] {p}")
            continue
        text = p.read_text(encoding="utf-8")
        lines = text.split("\n")
        new_lines, actions = repair_block(list(lines))
        changed = new_lines != lines
        if changed:
            changed_any = True
        print(f"[{'待修复' if changed else 'OK'}] {name}")
        for a in actions:
            print(f"    {a}")
        if not changed:
            n_key = sum(1 for ln in lines if KEY in ln)
            n_close = sum(1 for ln in lines if ln.strip() == "*/")
            print(f"    统计: KEY 行数={n_key}, 独立 '*/' 行数={n_close}")
        if apply and changed:
            p.write_text("\n".join(new_lines), encoding="utf-8")
            print(f"    已写入: {name}")
    print()
    if not apply:
        print("dry-run 结束。若输出全部为 OK,表示无需修复。")

if __name__ == "__main__":
    main()
