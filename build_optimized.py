import subprocess
import sys
import os

def build_executable():
    """构建优化的可执行文件"""
    # pyinstaller 命令参数 - 高度优化版本
    cmd = [
        'pyinstaller',
        '--noconfirm',  # 不需要确认
        '--onefile',  # 打包成单个exe文件
        '--windowed',  # 无控制台窗口
        '--name', 'MC自动寻路工具',  # exe文件名
        '--icon', 'NONE',  # 不使用图标
        # 排除不必要的模块以减小文件大小
        '--exclude-module', 'matplotlib',
        '--exclude-module', 'numpy',
        '--exclude-module', 'matplotlib.backends.backend_tags',
        '--exclude-module', 'PIL',
        '--exclude-module', 'pillow',
        '--exclude-module', 'scipy',
        '--exclude-module', 'pandas',
        '--exclude-module', 'requests',
        '--exclude-module', 'urllib3',
        '--exclude-module', 'certifi',
        '--exclude-module', 'chardet',
        '--exclude-module', 'idna',
        '--exclude-module', 'tkinter.test',
        '--exclude-module', 'unittest',
        '--exclude-module', 'email',
        '--exclude-module', 'http',
        '--exclude-module', 'xml',
        '--exclude-module', 'pydoc',
        '--exclude-module', 'doctest',
        '--exclude-module', 'argparse',
        '--exclude-module', 'difflib',
        '--exclude-module', 'inspect',
        '--exclude-module', 'pickle',
        '--exclude-module', 'sqlite3',
        '--exclude-module', 'ssl',
        '--exclude-module', 'html',
        # 注意：不要排除 'json' 模块，因为代码中使用了它
        'test_optimized.py'  # 源文件
    ]

    try:
        print("开始打包...")
        # 执行打包命令，添加编码处理
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
            encoding='utf-8',  # 指定编码
            errors='ignore'     # 忽略编码错误
        )
        print("打包成功！")
        print("EXE文件位于 dist 文件夹中")

        # 显示生成文件大小
        exe_path = os.path.join('dist', 'MC自动寻路工具.exe')
        if os.path.exists(exe_path):
            size = os.path.getsize(exe_path)
            print(f"生成文件大小: {size / 1024 / 1024:.2f} MB")

    except subprocess.CalledProcessError as e:
        print("打包失败！")
        print(f"错误信息: {e}")
        if e.output:
            print(f"详细输出: {e.output}")
    except Exception as e:
        print(f"发生错误: {e}")

def build_with_upx():
    """使用UPX压缩打包（需要先安装UPX）"""
    cmd = [
        'pyinstaller',
        '--noconfirm',
        '--onefile',
        '--windowed',
        '--name', 'MC自动寻路工具',
        '--icon', 'NONE',
        '--upx-dir', 'C:\\upx',  # 根据实际UPX安装路径修改
        '--exclude-module', 'matplotlib',
        '--exclude-module', 'numpy',
        '--exclude-module', 'PIL',
        '--exclude-module', 'tkinter.test',
        '--exclude-module', 'unittest',
        '--exclude-module', 'email',
        '--exclude-module', 'http',
        '--exclude-module', 'xml',
        # 注意：不要排除 'json' 模块，因为代码中使用了它
        'test_optimized.py'
    ]

    try:
        print("开始使用UPX压缩打包...")
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        print("打包成功！")
        print("EXE文件位于 dist 文件夹中")
    except subprocess.CalledProcessError as e:
        print("打包失败！请确保已安装UPX并正确设置路径")
        print(f"错误信息: {e}")
    except Exception as e:
        print(f"发生错误: {e}")

if __name__ == "__main__":
    print("选择打包方式:")
    print("1. 标准优化打包")
    print("2. UPX压缩打包（需要安装UPX）")

    try:
        choice = input("请输入选择 (1 或 2): ").strip()
    except:
        choice = "1"  # 默认选择

    if choice == "1":
        build_executable()
    elif choice == "2":
        build_with_upx()
    else:
        print("无效选择，使用标准优化打包")
        build_executable()
