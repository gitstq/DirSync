#!/usr/bin/env python3
"""
DirSync 单元测试
Unit Tests for DirSync
"""

import os
import sys
import tempfile
import shutil
import unittest
from pathlib import Path

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dirsync import DirSync, IgnorePattern, SyncMode, ConflictStrategy


class TestIgnorePattern(unittest.TestCase):
    """测试忽略模式"""
    
    def test_basic_patterns(self):
        """测试基本模式匹配"""
        ignore = IgnorePattern(["*.pyc", "__pycache__/", ".git/"])
        
        self.assertTrue(ignore.should_ignore("test.pyc"))
        self.assertTrue(ignore.should_ignore("__pycache__", is_dir=True))
        self.assertTrue(ignore.should_ignore(".git", is_dir=True))
        self.assertFalse(ignore.should_ignore("test.py"))
        self.assertFalse(ignore.should_ignore("src", is_dir=True))
    
    def test_negation(self):
        """测试否定模式"""
        ignore = IgnorePattern(["*.log", "!important.log"])
        
        self.assertTrue(ignore.should_ignore("debug.log"))
        self.assertFalse(ignore.should_ignore("important.log"))
    
    def test_comments_and_empty(self):
        """测试注释和空行"""
        ignore = IgnorePattern(["", "# This is a comment", "*.tmp"])
        
        self.assertTrue(ignore.should_ignore("file.tmp"))
        self.assertFalse(ignore.should_ignore("# This is a comment"))


class TestDirSync(unittest.TestCase):
    """测试 DirSync 核心功能"""
    
    def setUp(self):
        """设置测试环境"""
        self.temp_dir = tempfile.mkdtemp()
        self.source_dir = Path(self.temp_dir) / "source"
        self.target_dir = Path(self.temp_dir) / "target"
        self.source_dir.mkdir()
        self.target_dir.mkdir()
    
    def tearDown(self):
        """清理测试环境"""
        shutil.rmtree(self.temp_dir)
    
    def create_test_files(self):
        """创建测试文件"""
        # 源目录文件
        (self.source_dir / "file1.txt").write_text("content1")
        (self.source_dir / "file2.txt").write_text("content2")
        
        # 子目录
        (self.source_dir / "subdir").mkdir()
        (self.source_dir / "subdir" / "file3.txt").write_text("content3")
        
        # 目标目录文件（部分相同，部分不同）
        (self.target_dir / "file1.txt").write_text("content1")  # 相同
        (self.target_dir / "file2.txt").write_text("different")  # 不同
        (self.target_dir / "file4.txt").write_text("only_in_target")  # 仅在目标
    
    def test_compare_directories(self):
        """测试目录对比"""
        self.create_test_files()
        
        sync = DirSync(str(self.source_dir), str(self.target_dir), use_hash=False)
        diff = sync.compare()
        
        # 验证结果
        self.assertIn("file1.txt", diff.identical)
        self.assertIn("file2.txt", [m[0] for m in diff.modified])
        self.assertIn("subdir/file3.txt", diff.only_in_source)
        self.assertIn("file4.txt", diff.only_in_target)
    
    def test_sync_update_mode(self):
        """测试更新模式同步"""
        self.create_test_files()
        
        sync = DirSync(str(self.source_dir), str(self.target_dir), use_hash=False)
        result = sync.sync(mode=SyncMode.UPDATE, dry_run=False)
        
        # 验证文件已复制
        self.assertTrue((self.target_dir / "subdir" / "file3.txt").exists())
        self.assertEqual((self.target_dir / "file2.txt").read_text(), "content2")
        
        # 验证目标特有文件未被删除
        self.assertTrue((self.target_dir / "file4.txt").exists())
    
    def test_sync_mirror_mode(self):
        """测试镜像模式同步"""
        self.create_test_files()
        
        sync = DirSync(str(self.source_dir), str(self.target_dir), use_hash=False)
        result = sync.sync(mode=SyncMode.MIRROR, dry_run=False)
        
        # 验证文件已复制
        self.assertTrue((self.target_dir / "subdir" / "file3.txt").exists())
        
        # 验证目标特有文件已被删除
        self.assertFalse((self.target_dir / "file4.txt").exists())
    
    def test_dry_run_mode(self):
        """测试预览模式"""
        self.create_test_files()
        
        sync = DirSync(str(self.source_dir), str(self.target_dir), use_hash=False)
        result = sync.sync(mode=SyncMode.UPDATE, dry_run=True)
        
        # 验证文件未被实际修改
        self.assertFalse((self.target_dir / "file3.txt").exists())
        self.assertEqual((self.target_dir / "file2.txt").read_text(), "different")
    
    def test_ignore_patterns(self):
        """测试忽略模式"""
        # 创建包含忽略文件的测试结构
        (self.source_dir / "keep.txt").write_text("keep")
        (self.source_dir / "ignore.tmp").write_text("ignore")
        (self.source_dir / "__pycache__").mkdir()
        (self.source_dir / "__pycache__" / "cache.pyc").write_text("cache")
        
        sync = DirSync(
            str(self.source_dir), 
            str(self.target_dir),
            ignore_patterns=["*.tmp", "__pycache__/"],
            use_hash=False
        )
        diff = sync.compare()
        
        # 验证忽略的文件不在差异列表中
        self.assertNotIn("ignore.tmp", diff.only_in_source)
        self.assertNotIn("__pycache__/cache.pyc", diff.only_in_source)
        self.assertIn("keep.txt", diff.only_in_source)
    
    def test_empty_directories(self):
        """测试空目录处理"""
        (self.source_dir / "empty_dir").mkdir()
        (self.source_dir / "file.txt").write_text("content")
        
        sync = DirSync(str(self.source_dir), str(self.target_dir), use_hash=False)
        diff = sync.compare()
        
        self.assertIn("empty_dir", diff.only_in_source)
        self.assertIn("file.txt", diff.only_in_source)


class TestFileInfo(unittest.TestCase):
    """测试文件信息类"""
    
    def test_file_info_creation(self):
        """测试文件信息创建"""
        import tempfile
        import time
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("test content")
            temp_path = f.name
        
        try:
            from dirsync import FileInfo
            info = FileInfo(
                path="test.txt",
                size=12,
                mtime=time.time(),
                md5="abc123",
                is_dir=False
            )
            
            self.assertEqual(info.path, "test.txt")
            self.assertEqual(info.size, 12)
            self.assertEqual(info.md5, "abc123")
            self.assertFalse(info.is_dir)
        finally:
            os.unlink(temp_path)


class TestCLI(unittest.TestCase):
    """测试命令行接口"""
    
    def test_argument_parser(self):
        """测试参数解析器创建"""
        from dirsync import create_cli
        
        parser = create_cli()
        self.assertIsNotNone(parser)
    
    def test_version_flag(self):
        """测试版本标志"""
        from dirsync import create_cli, __version__
        
        parser = create_cli()
        
        # 测试版本参数
        with self.assertRaises(SystemExit) as cm:
            parser.parse_args(["--version"])
        
        self.assertEqual(cm.exception.code, 0)


def run_tests():
    """运行所有测试"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加测试类
    suite.addTests(loader.loadTestsFromTestCase(TestIgnorePattern))
    suite.addTests(loader.loadTestsFromTestCase(TestDirSync))
    suite.addTests(loader.loadTestsFromTestCase(TestFileInfo))
    suite.addTests(loader.loadTestsFromTestCase(TestCLI))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(run_tests())
