#!/usr/bin/env python3
"""
DirSync - 轻量级智能目录对比与同步引擎
Lightweight Intelligent Directory Comparison & Synchronization Engine

A zero-dependency CLI tool for intelligent directory comparison and synchronization.
"""

import os
import sys
import hashlib
import argparse
import fnmatch
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, asdict
from enum import Enum

__version__ = "1.0.0"
__author__ = "DirSync Team"


class SyncMode(Enum):
    """同步模式"""
    MIRROR = "mirror"      # 镜像模式：目标与源完全一致
    UPDATE = "update"      # 更新模式：仅复制新文件和修改过的文件
    BIDIRECTIONAL = "bidirectional"  # 双向同步


class ConflictStrategy(Enum):
    """冲突解决策略"""
    SOURCE_WINS = "source"     # 源目录优先
    TARGET_WINS = "target"     # 目标目录优先
    NEWER_WINS = "newer"       # 较新文件优先
    LARGER_WINS = "larger"     # 较大文件优先
    SKIP = "skip"              # 跳过冲突
    PROMPT = "prompt"          # 交互式提示


@dataclass
class FileInfo:
    """文件信息数据类"""
    path: str
    size: int
    mtime: float
    md5: Optional[str] = None
    is_dir: bool = False
    
    def to_dict(self) -> dict:
        return {
            "path": self.path,
            "size": self.size,
            "mtime": self.mtime,
            "md5": self.md5,
            "is_dir": self.is_dir
        }


@dataclass
class DiffResult:
    """差异结果数据类"""
    only_in_source: List[str]
    only_in_target: List[str]
    modified: List[Tuple[str, FileInfo, FileInfo]]  # path, source_info, target_info
    identical: List[str]
    conflicts: List[Tuple[str, FileInfo, FileInfo]]
    
    def to_dict(self) -> dict:
        return {
            "only_in_source": self.only_in_source,
            "only_in_target": self.only_in_target,
            "modified": [(p, s.to_dict(), t.to_dict()) for p, s, t in self.modified],
            "identical": self.identical,
            "conflicts": [(p, s.to_dict(), t.to_dict()) for p, s, t in self.conflicts]
        }


class IgnorePattern:
    """.gitignore风格的忽略模式处理器"""
    
    def __init__(self, patterns: List[str] = None):
        self.patterns = patterns or []
        self.negations = []
        self._parse_patterns()
    
    def _parse_patterns(self):
        """解析忽略模式"""
        self.negations = []
        clean_patterns = []
        for pattern in self.patterns:
            pattern = pattern.strip()
            if not pattern or pattern.startswith('#'):
                continue
            if pattern.startswith('!'):
                self.negations.append(pattern[1:])
            else:
                clean_patterns.append(pattern)
        self.patterns = clean_patterns
    
    def should_ignore(self, path: str, is_dir: bool = False) -> bool:
        """检查路径是否应该被忽略"""
        path = path.replace(os.sep, '/')
        
        # 检查否定模式
        for neg_pattern in self.negations:
            if fnmatch.fnmatch(path, neg_pattern) or \
               fnmatch.fnmatch(os.path.basename(path), neg_pattern):
                return False
        
        # 检查忽略模式
        for pattern in self.patterns:
            # 目录模式
            if pattern.endswith('/'):
                if is_dir and (fnmatch.fnmatch(path, pattern[:-1]) or 
                              fnmatch.fnmatch(path, pattern[:-1] + '/*')):
                    return True
            # 通配符匹配
            elif fnmatch.fnmatch(path, pattern) or \
                 fnmatch.fnmatch(os.path.basename(path), pattern):
                return True
            # 递归匹配
            elif pattern.startswith('**/') and fnmatch.fnmatch(path, pattern[3:]):
                return True
        
        return False


class DirSync:
    """目录同步核心类"""
    
    def __init__(self, source: str, target: str, 
                 ignore_patterns: List[str] = None,
                 use_hash: bool = True,
                 progress_callback = None):
        self.source = Path(source).resolve()
        self.target = Path(target).resolve()
        self.ignore = IgnorePattern(ignore_patterns or [])
        self.use_hash = use_hash
        self.progress_callback = progress_callback
        self.stats = {
            "files_scanned": 0,
            "dirs_scanned": 0,
            "files_copied": 0,
            "files_deleted": 0,
            "bytes_transferred": 0,
            "errors": []
        }
    
    def _calculate_md5(self, filepath: str) -> str:
        """计算文件MD5哈希值"""
        hash_md5 = hashlib.md5()
        try:
            with open(filepath, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    hash_md5.update(chunk)
        except Exception as e:
            self.stats["errors"].append(f"Hash error for {filepath}: {e}")
            return ""
        return hash_md5.hexdigest()
    
    def _get_file_info(self, filepath: str, base_path: Path) -> Optional[FileInfo]:
        """获取文件信息"""
        try:
            rel_path = str(Path(filepath).relative_to(base_path))
            stat = os.stat(filepath)
            is_dir = os.path.isdir(filepath)
            
            md5 = None
            if self.use_hash and not is_dir:
                md5 = self._calculate_md5(filepath)
            
            return FileInfo(
                path=rel_path,
                size=stat.st_size if not is_dir else 0,
                mtime=stat.st_mtime,
                md5=md5,
                is_dir=is_dir
            )
        except Exception as e:
            self.stats["errors"].append(f"Stat error for {filepath}: {e}")
            return None
    
    def _scan_directory(self, directory: Path) -> Dict[str, FileInfo]:
        """扫描目录获取所有文件信息"""
        files = {}
        
        for root, dirs, filenames in os.walk(directory):
            root_path = Path(root)
            rel_root = root_path.relative_to(directory)
            
            # 过滤目录
            dirs[:] = [d for d in dirs if not self.ignore.should_ignore(
                str(rel_root / d) if str(rel_root) != '.' else d, is_dir=True)]
            
            for d in dirs:
                dir_path = root_path / d
                rel_path = str(dir_path.relative_to(directory))
                if not self.ignore.should_ignore(rel_path, is_dir=True):
                    info = self._get_file_info(str(dir_path), directory)
                    if info:
                        files[rel_path] = info
                        self.stats["dirs_scanned"] += 1
            
            for filename in filenames:
                file_path = root_path / filename
                rel_path = str(file_path.relative_to(directory))
                
                if not self.ignore.should_ignore(rel_path):
                    info = self._get_file_info(str(file_path), directory)
                    if info:
                        files[rel_path] = info
                        self.stats["files_scanned"] += 1
                        
                        if self.progress_callback:
                            self.progress_callback(f"Scanned: {rel_path}")
        
        return files
    
    def compare(self) -> DiffResult:
        """对比源目录和目标目录"""
        source_files = self._scan_directory(self.source)
        target_files = self._scan_directory(self.target)
        
        only_in_source = []
        only_in_target = []
        modified = []
        identical = []
        conflicts = []
        
        # 检查源目录中的文件
        for rel_path, source_info in source_files.items():
            if rel_path not in target_files:
                only_in_source.append(rel_path)
            else:
                target_info = target_files[rel_path]
                
                # 检查是否相同
                if source_info.is_dir and target_info.is_dir:
                    identical.append(rel_path)
                elif source_info.size == target_info.size:
                    if self.use_hash and source_info.md5 and target_info.md5:
                        if source_info.md5 == target_info.md5:
                            identical.append(rel_path)
                        else:
                            modified.append((rel_path, source_info, target_info))
                    elif abs(source_info.mtime - target_info.mtime) < 1:
                        identical.append(rel_path)
                    else:
                        modified.append((rel_path, source_info, target_info))
                else:
                    modified.append((rel_path, source_info, target_info))
        
        # 检查仅在目标目录中的文件
        for rel_path in target_files:
            if rel_path not in source_files:
                only_in_target.append(rel_path)
        
        # 检测冲突（双向同步时）
        for rel_path, source_info in source_files.items():
            if rel_path in target_files:
                target_info = target_files[rel_path]
                if not source_info.is_dir and not target_info.is_dir:
                    if source_info.mtime != target_info.mtime and \
                       source_info.size != target_info.size:
                        conflicts.append((rel_path, source_info, target_info))
        
        return DiffResult(
            only_in_source=only_in_source,
            only_in_target=only_in_target,
            modified=modified,
            identical=identical,
            conflicts=conflicts
        )
    
    def _copy_file(self, src: str, dst: str) -> bool:
        """复制文件并保留元数据"""
        try:
            import shutil
            
            # 如果是目录，创建目录
            if os.path.isdir(src):
                if not os.path.exists(dst):
                    os.makedirs(dst, exist_ok=True)
                return True
            
            # 复制文件
            dst_dir = os.path.dirname(dst)
            if dst_dir and not os.path.exists(dst_dir):
                os.makedirs(dst_dir, exist_ok=True)
            
            shutil.copy2(src, dst)
            self.stats["files_copied"] += 1
            self.stats["bytes_transferred"] += os.path.getsize(src)
            return True
        except Exception as e:
            self.stats["errors"].append(f"Copy error {src} -> {dst}: {e}")
            return False
    
    def _delete_file(self, path: str) -> bool:
        """删除文件或目录"""
        try:
            if os.path.isdir(path):
                import shutil
                shutil.rmtree(path)
            else:
                os.remove(path)
            self.stats["files_deleted"] += 1
            return True
        except Exception as e:
            self.stats["errors"].append(f"Delete error {path}: {e}")
            return False
    
    def sync(self, mode: SyncMode = SyncMode.UPDATE, 
             conflict_strategy: ConflictStrategy = ConflictStrategy.NEWER_WINS,
             dry_run: bool = False) -> Dict:
        """执行同步操作"""
        diff = self.compare()
        operations = []
        
        if mode == SyncMode.MIRROR:
            # 镜像模式：使目标与源完全一致
            # 1. 复制新文件和修改的文件
            for rel_path in diff.only_in_source:
                src = self.source / rel_path
                dst = self.target / rel_path
                operations.append(("COPY", str(src), str(dst)))
            
            for rel_path, src_info, tgt_info in diff.modified:
                src = self.source / rel_path
                dst = self.target / rel_path
                operations.append(("COPY", str(src), str(dst)))
            
            # 2. 删除目标中多余的文件
            for rel_path in diff.only_in_target:
                dst = self.target / rel_path
                operations.append(("DELETE", str(dst), None))
                
        elif mode == SyncMode.UPDATE:
            # 更新模式：仅复制新文件和修改的文件
            for rel_path in diff.only_in_source:
                src = self.source / rel_path
                dst = self.target / rel_path
                operations.append(("COPY", str(src), str(dst)))
            
            for rel_path, src_info, tgt_info in diff.modified:
                src = self.source / rel_path
                dst = self.target / rel_path
                operations.append(("COPY", str(src), str(dst)))
                
        elif mode == SyncMode.BIDIRECTIONAL:
            # 双向同步
            # 复制源到目标
            for rel_path in diff.only_in_source:
                src = self.source / rel_path
                dst = self.target / rel_path
                operations.append(("COPY", str(src), str(dst)))
            
            # 复制目标到源
            for rel_path in diff.only_in_target:
                src = self.target / rel_path
                dst = self.source / rel_path
                operations.append(("COPY", str(src), str(dst)))
            
            # 处理冲突
            for rel_path, src_info, tgt_info in diff.conflicts:
                should_copy_src = False
                
                if conflict_strategy == ConflictStrategy.SOURCE_WINS:
                    should_copy_src = True
                elif conflict_strategy == ConflictStrategy.TARGET_WINS:
                    should_copy_src = False
                elif conflict_strategy == ConflictStrategy.NEWER_WINS:
                    should_copy_src = src_info.mtime > tgt_info.mtime
                elif conflict_strategy == ConflictStrategy.LARGER_WINS:
                    should_copy_src = src_info.size > tgt_info.size
                
                if should_copy_src:
                    src = self.source / rel_path
                    dst = self.target / rel_path
                    operations.append(("COPY", str(src), str(dst)))
                else:
                    src = self.target / rel_path
                    dst = self.source / rel_path
                    operations.append(("COPY", str(src), str(dst)))
        
        # 执行操作
        if not dry_run:
            for op, src, dst in operations:
                if op == "COPY":
                    self._copy_file(src, dst)
                elif op == "DELETE":
                    self._delete_file(src)
                
                if self.progress_callback:
                    self.progress_callback(f"{op}: {src}")
        
        return {
            "operations": operations,
            "stats": self.stats,
            "diff": diff
        }
    
    def generate_report(self, diff: DiffResult, format: str = "text") -> str:
        """生成对比报告"""
        if format == "json":
            return json.dumps(diff.to_dict(), indent=2)
        
        lines = [
            "=" * 60,
            "DirSync 对比报告 / Comparison Report",
            "=" * 60,
            f"生成时间 / Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"源目录 / Source: {self.source}",
            f"目标目录 / Target: {self.target}",
            "-" * 60,
            "",
            f"📁 仅在源目录 / Only in Source: {len(diff.only_in_source)} 项",
            "-" * 40,
        ]
        
        for path in sorted(diff.only_in_source)[:20]:
            lines.append(f"  + {path}")
        if len(diff.only_in_source) > 20:
            lines.append(f"  ... 还有 {len(diff.only_in_source) - 20} 项")
        
        lines.extend([
            "",
            f"📁 仅在目标目录 / Only in Target: {len(diff.only_in_target)} 项",
            "-" * 40,
        ])
        
        for path in sorted(diff.only_in_target)[:20]:
            lines.append(f"  - {path}")
        if len(diff.only_in_target) > 20:
            lines.append(f"  ... 还有 {len(diff.only_in_target) - 20} 项")
        
        lines.extend([
            "",
            f"📝 已修改 / Modified: {len(diff.modified)} 项",
            "-" * 40,
        ])
        
        for path, src_info, tgt_info in sorted(diff.modified, key=lambda x: x[0])[:20]:
            lines.append(f"  ~ {path}")
            lines.append(f"    Source: {src_info.size} bytes, {datetime.fromtimestamp(src_info.mtime)}")
            lines.append(f"    Target: {tgt_info.size} bytes, {datetime.fromtimestamp(tgt_info.mtime)}")
        if len(diff.modified) > 20:
            lines.append(f"  ... 还有 {len(diff.modified) - 20} 项")
        
        lines.extend([
            "",
            f"✅ 完全相同 / Identical: {len(diff.identical)} 项",
            "-" * 40,
        ])
        
        if diff.conflicts:
            lines.extend([
                "",
                f"⚠️  冲突 / Conflicts: {len(diff.conflicts)} 项",
                "-" * 40,
            ])
            for path, src_info, tgt_info in diff.conflicts[:10]:
                lines.append(f"  ! {path}")
        
        lines.extend([
            "",
            "=" * 60,
            f"扫描统计 / Scan Statistics:",
            f"  文件 / Files: {self.stats['files_scanned']}",
            f"  目录 / Directories: {self.stats['dirs_scanned']}",
            "=" * 60,
        ])
        
        return "\n".join(lines)


def create_cli():
    """创建命令行界面"""
    parser = argparse.ArgumentParser(
        prog="dirsync",
        description="DirSync - 轻量级智能目录对比与同步引擎",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例 / Examples:
  %(prog)s compare /path/to/source /path/to/target
  %(prog)s sync /path/to/source /path/to/target --mode mirror
  %(prog)s sync /path/to/source /path/to/target --mode update --dry-run
  %(prog)s sync /path/to/source /path/to/target --mode bidirectional
        """
    )
    
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令 / Available commands")
    
    # compare 命令
    compare_parser = subparsers.add_parser("compare", help="对比两个目录 / Compare two directories")
    compare_parser.add_argument("source", help="源目录 / Source directory")
    compare_parser.add_argument("target", help="目标目录 / Target directory")
    compare_parser.add_argument("-i", "--ignore", action="append", default=[],
                               help="忽略模式 / Ignore patterns (可多次使用)")
    compare_parser.add_argument("--no-hash", action="store_true",
                               help="不使用哈希对比 / Don't use hash comparison")
    compare_parser.add_argument("-o", "--output", help="输出报告到文件 / Output report to file")
    compare_parser.add_argument("--format", choices=["text", "json"], default="text",
                               help="报告格式 / Report format")
    
    # sync 命令
    sync_parser = subparsers.add_parser("sync", help="同步目录 / Synchronize directories")
    sync_parser.add_argument("source", help="源目录 / Source directory")
    sync_parser.add_argument("target", help="目标目录 / Target directory")
    sync_parser.add_argument("-m", "--mode", choices=["mirror", "update", "bidirectional"],
                            default="update", help="同步模式 / Sync mode")
    sync_parser.add_argument("--conflict", 
                            choices=["source", "target", "newer", "larger", "skip", "prompt"],
                            default="newer", help="冲突解决策略 / Conflict resolution strategy")
    sync_parser.add_argument("-i", "--ignore", action="append", default=[],
                            help="忽略模式 / Ignore patterns")
    sync_parser.add_argument("--no-hash", action="store_true",
                            help="不使用哈希对比 / Don't use hash comparison")
    sync_parser.add_argument("-n", "--dry-run", action="store_true",
                            help="预览模式（不实际执行）/ Dry run (preview only)")
    sync_parser.add_argument("-v", "--verbose", action="store_true",
                            help="详细输出 / Verbose output")
    
    # init 命令
    init_parser = subparsers.add_parser("init", help="初始化忽略文件 / Initialize ignore file")
    init_parser.add_argument("path", nargs="?", default=".", 
                            help="目录路径 / Directory path")
    
    return parser


def main():
    """主函数"""
    parser = create_cli()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    if args.command == "init":
        # 创建默认的 .dirsyncignore 文件
        ignore_file = Path(args.path) / ".dirsyncignore"
        default_patterns = """# DirSync 忽略规则 / DirSync Ignore Rules
# 语法与 .gitignore 相同 / Syntax same as .gitignore

# 版本控制 / Version Control
.git
.svn
.hg

# 依赖目录 / Dependencies
node_modules
vendor
__pycache__
*.pyc
.pytest_cache

# IDE 配置 / IDE Config
.idea
.vscode
*.swp
*.swo
*~

# 操作系统文件 / OS Files
.DS_Store
Thumbs.db
desktop.ini

# 日志和临时文件 / Logs & Temp
*.log
*.tmp
tmp/
temp/
"""
        if ignore_file.exists():
            print(f"⚠️  文件已存在 / File already exists: {ignore_file}")
        else:
            ignore_file.write_text(default_patterns)
            print(f"✅ 已创建 / Created: {ignore_file}")
        return 0
    
    # 检查目录是否存在
    if not os.path.isdir(args.source):
        print(f"❌ 错误 / Error: 源目录不存在 / Source directory does not exist: {args.source}")
        return 1
    
    if not os.path.isdir(args.target):
        if args.command == "sync" and not args.dry_run:
            print(f"📁 创建目标目录 / Creating target directory: {args.target}")
            os.makedirs(args.target, exist_ok=True)
        else:
            print(f"❌ 错误 / Error: 目标目录不存在 / Target directory does not exist: {args.target}")
            return 1
    
    # 读取忽略文件
    ignore_patterns = list(args.ignore)
    ignore_file = Path(args.source) / ".dirsyncignore"
    if ignore_file.exists():
        ignore_patterns.extend(ignore_file.read_text().splitlines())
    
    # 进度回调
    def progress(msg):
        verbose = getattr(args, 'verbose', False)
        if verbose or args.command == "compare":
            print(f"  {msg}")
    
    # 创建同步器
    sync = DirSync(
        source=args.source,
        target=args.target,
        ignore_patterns=ignore_patterns,
        use_hash=not args.no_hash,
        progress_callback=progress
    )
    
    if args.command == "compare":
        print(f"🔍 正在对比目录 / Comparing directories...")
        print(f"   源 / Source: {args.source}")
        print(f"   目标 / Target: {args.target}")
        print()
        
        diff = sync.compare()
        report = sync.generate_report(diff, format=args.format)
        
        if args.output:
            Path(args.output).write_text(report)
            print(f"✅ 报告已保存 / Report saved: {args.output}")
        else:
            print(report)
        
        # 返回码：有差异返回1，无差异返回0
        has_diff = diff.only_in_source or diff.only_in_target or diff.modified
        return 1 if has_diff else 0
    
    elif args.command == "sync":
        mode = SyncMode(args.mode)
        conflict = ConflictStrategy(args.conflict)
        
        print(f"🔄 正在同步 / Synchronizing...")
        print(f"   模式 / Mode: {mode.value}")
        print(f"   源 / Source: {args.source}")
        print(f"   目标 / Target: {args.target}")
        
        if args.dry_run:
            print(f"   ⚠️  预览模式 / Dry run mode - 不会实际修改文件 / No files will be modified")
        print()
        
        result = sync.sync(mode=mode, conflict_strategy=conflict, dry_run=args.dry_run)
        
        print(f"\n📊 同步统计 / Sync Statistics:")
        print(f"   操作数 / Operations: {len(result['operations'])}")
        print(f"   文件复制 / Files copied: {sync.stats['files_copied']}")
        print(f"   文件删除 / Files deleted: {sync.stats['files_deleted']}")
        print(f"   传输字节 / Bytes transferred: {sync.stats['bytes_transferred']:,}")
        
        if sync.stats['errors']:
            print(f"\n⚠️  错误 / Errors ({len(sync.stats['errors'])}):")
            for error in sync.stats['errors'][:10]:
                print(f"   - {error}")
        
        if args.dry_run:
            print(f"\n📋 预览操作 / Preview Operations:")
            for op, src, dst in result['operations'][:20]:
                if dst:
                    print(f"   {op}: {src} -> {dst}")
                else:
                    print(f"   {op}: {src}")
            if len(result['operations']) > 20:
                print(f"   ... 还有 {len(result['operations']) - 20} 项操作")
        
        return 0
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
