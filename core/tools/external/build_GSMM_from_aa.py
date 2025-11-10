#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
批量将 .aa/.faa 氨基酸序列文件构建为基因组规模代谢模型（SBML .xml）
- 必选：--input_path 指向包含 .aa/.faa 的文件夹
- 可选：--genomes_path 指向包含 .fa/.fna 的基因组文件夹，先用 Prodigal 生成 .aa 再构建
- 依赖：carveme（提供 carve 命令），可选 prodigal（提供 prodigal 命令）
"""

from __future__ import annotations

import argparse
import concurrent.futures as cf
import subprocess
import sys
import shutil
import os
from pathlib import Path
from datetime import datetime


# ---------------------------
# 工具可用性检查
# ---------------------------
def which_or_none(cmd: str):
    return shutil.which(cmd)


def ensure_cmd(cmd: str, friendly_name: str) -> str:
    path = which_or_none(cmd)
    if path is None:
        raise RuntimeError(f"没有在 PATH 中找到 {friendly_name}（命令: {cmd}），请先安装并确保可执行。")
    return path


# ---------------------------
# Prodigal：基因组 -> .aa
# ---------------------------
def run_prodigal_on_genome(
    genome_path: Path,
    aa_out_dir: Path,
    prodigal_cmd: str,
    prodigal_mode: str = "meta",
) -> Path:
    aa_out_dir.mkdir(parents=True, exist_ok=True)
    stem = genome_path.stem
    aa_out = aa_out_dir / f"{stem}.aa"

    cmd = [
        prodigal_cmd,
        "-i",
        str(genome_path),
        "-a",
        str(aa_out),
        "-p",
        prodigal_mode,
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return aa_out


def batch_prodigal(
    genomes_dir: Path,
    aa_dir: Path,
    prodigal_cmd: str,
    prodigal_mode: str,
    threads: int,
):
    genomes: list[Path] = []
    for ext in (".fa", ".fna", ".fasta", ".fas"):
        genomes += list(genomes_dir.glob(f"*{ext}"))
    if not genomes:
        print(f"[WARN] {genomes_dir} 中未找到基因组文件（.fa/.fna/.fasta）", flush=True)
        return []

    ensure_cmd(prodigal_cmd, "Prodigal")

    def _worker(g: Path):
        try:
            aa = run_prodigal_on_genome(g, aa_dir, prodigal_cmd, prodigal_mode)
            return (g, aa, None)
        except subprocess.CalledProcessError as e:
            return (g, None, f"Prodigal 失败: {e.stderr.decode(errors='ignore')[:500]}")
        except Exception as e:  # noqa: BLE001
            return (g, None, str(e))

    results = []
    with cf.ThreadPoolExecutor(max_workers=threads) as ex:
        for g, aa, err in ex.map(_worker, genomes):
            if err:
                print(f"[ERROR] {g.name}: {err}", flush=True)
            else:
                print(f"[OK] Prodigal 生成: {aa.name}", flush=True)
                results.append(aa)
    return results


# ---------------------------
# CarveMe：.aa/.faa -> .xml
# ---------------------------
def run_carveme(
    aa_path: Path,
    out_dir: Path,
    carve_cmd: str,
    extra_args: list[str] | None = None,
    overwrite: bool = False,
):
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = aa_path.stem
    out_xml = out_dir / f"{stem}.xml"

    if out_xml.exists() and not overwrite:
        return (aa_path, out_xml, "skip")

    cmd = [carve_cmd, str(aa_path), "-o", str(out_xml)]
    if extra_args:
        cmd += extra_args

    completed = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if completed.returncode != 0:
        raise subprocess.CalledProcessError(
            completed.returncode,
            cmd,
            output=completed.stdout,
            stderr=completed.stderr,
        )
    return (aa_path, out_xml, "built")


def batch_carveme(
    aa_dir: Path,
    out_dir: Path,
    carve_cmd: str,
    threads: int,
    overwrite: bool,
    aa_exts: tuple[str, ...] = (".aa", ".faa"),
    extra_args: list[str] | None = None,
):
    ensure_cmd(carve_cmd, "CarveMe（carve）")

    aa_files: list[Path] = []
    for ext in aa_exts:
        aa_files += list(aa_dir.glob(f"*{ext}"))
    if not aa_files:
        print(f"[WARN] {aa_dir} 中未找到 .aa/.faa", flush=True)
        return

    def _worker(aa: Path):
        try:
            aa_p, out_xml, status = run_carveme(
                aa,
                out_dir,
                carve_cmd,
                extra_args=extra_args,
                overwrite=overwrite,
            )
            return (aa_p, out_xml, status, None)
        except subprocess.CalledProcessError as e:
            return (aa, None, "error", f"CarveMe 失败: {e.stderr[:800]}")
        except Exception as e:  # noqa: BLE001
            return (aa, None, "error", str(e))

    built = skipped = failed = 0
    with cf.ThreadPoolExecutor(max_workers=threads) as ex:
        for aa_p, out_xml, status, err in ex.map(_worker, aa_files):
            if status == "built":
                built += 1
                print(f"[OK] 构建完成: {aa_p.name} -> {out_xml.name}", flush=True)
            elif status == "skip":
                skipped += 1
                print(f"[SKIP] 已存在，跳过: {out_dir / (aa_p.stem + '.xml')}", flush=True)
            else:
                failed += 1
                print(f"[ERROR] {aa_p.name}: {err}", flush=True)

    print(f"\n[SUMMARY] CarveMe 构建完成 | 新建: {built}, 跳过: {skipped}, 失败: {failed}")


# ---------------------------
# 主流程
# ---------------------------
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="从 .aa/.faa 批量构建 GSMM（可选从基因组先跑 Prodigal 再构建）"
    )
    parser.add_argument("--input_path", required=True, help="包含 .aa/.faa 的目录路径")
    parser.add_argument("--output_path", required=True, help="输出 SBML(.xml) 的目录")
    parser.add_argument("--threads", type=int, default=4, help="并行线程数（默认 4）")
    parser.add_argument("--overwrite", action="store_true", help="已存在同名 .xml 时是否覆盖")
    parser.add_argument("--carve_cmd", default="carve", help="CarveMe 可执行命令名（默认 carve）")
    parser.add_argument(
        "--carve_extra",
        nargs=argparse.REMAINDER,
        help="透传给 carve 的额外参数（写在 --carve_extra 后面的都会传给 carve）",
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="占位参数，与旧版调用兼容；当前无需额外操作",
    )
    parser.add_argument("--genomes_path", help="（可选）包含 .fa/.fna 的目录，先用 Prodigal 生成 .aa")
    parser.add_argument("--prodigal_cmd", default="prodigal", help="Prodigal 命令名（默认 prodigal）")
    parser.add_argument(
        "--prodigal_mode",
        default="meta",
        choices=["meta", "single"],
        help="Prodigal -p 选项（默认 meta）",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    input_dir = Path(args.input_path).expanduser().resolve()
    out_dir = Path(args.output_path).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始执行")
    print(f"- 输入（.aa/.faa）目录: {input_dir}")
    print(f"- 输出（.xml）目录   : {out_dir}")
    print(f"- 线程数            : {args.threads}")
    if args.validate:
        print("- 已启用 validate 占位参数（当前不执行额外校验）")

    if args.genomes_path:
        genomes_dir = Path(args.genomes_path).expanduser().resolve()
        print(f"- 基因组目录（可选）: {genomes_dir}")
        batch_prodigal(
            genomes_dir=genomes_dir,
            aa_dir=input_dir,
            prodigal_cmd=args.prodigal_cmd,
            prodigal_mode=args.prodigal_mode,
            threads=args.threads,
        )

    batch_carveme(
        aa_dir=input_dir,
        out_dir=out_dir,
        carve_cmd=args.carve_cmd,
        threads=args.threads,
        overwrite=args.overwrite,
        aa_exts=(".aa", ".faa"),
        extra_args=args.carve_extra,
    )


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as exc:  # pragma: no cover - CLI 直接退出
        print(f"[FATAL] {exc}", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:  # pragma: no cover - CLI 直接退出
        print(f"[FATAL] 未知错误: {exc}", file=sys.stderr)
        sys.exit(2)
