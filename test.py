import subprocess
import sys


def check_migration_status():
    print("检查迁移状态...\n")

    # 检查所有应用
    result = subprocess.run(
        [sys.executable, "manage.py", "showmigrations"],
        capture_output=True,
        text=True
    )

    print(result.stdout)

    # 检查是否有未应用的迁移
    if "[ ]" in result.stdout:
        print("⚠️  有未应用的迁移！")
        print("运行以下命令：")
        print("  python manage.py migrate")
        return False
    else:
        print("✅ 所有迁移已应用")
        return True


if __name__ == "__main__":
    check_migration_status()