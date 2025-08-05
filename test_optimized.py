import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import threading
import time
import pyautogui
import json
import os


class MinecraftAutoGotoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MC自动寻路配置系统")
        self.root.geometry("650x450")
        self.is_running = False
        self.cycle_count = 0
        self.total_cycles = 0
        self.route_points = []  # 存储所有路线点
        self.config_file = "mc_route_config.json"  # 默认配置文件

        # 初始化UI组件
        self.create_widgets()

        # 尝试加载默认配置文件
        self.load_config(self.config_file)

        # 如果没有加载到配置，则添加默认示例点
        if not self.route_points:
            self.add_example_points()

        # 安全提示
        self.show_safety_warning()

    def create_widgets(self):
        """创建UI界面组件"""
        # 创建菜单栏
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="新建配置", command=self.new_config)
        file_menu.add_command(label="打开配置", command=self.open_config)
        file_menu.add_command(label="保存配置", command=self.save_config)
        file_menu.add_command(label="另存为", command=self.save_config_as)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.root.quit)

        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 左侧：路线点管理
        left_frame = ttk.LabelFrame(main_frame, text="路线点配置", padding=10)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        # 路线点列表
        columns = ("#", "坐标", "等待时间(s)", "描述")
        self.points_tree = ttk.Treeview(left_frame, columns=columns, show="headings", height=10)

        for col in columns:
            self.points_tree.heading(col, text=col)
            self.points_tree.column(col, width=80, anchor=tk.CENTER)

        self.points_tree.column("#", width=40)
        self.points_tree.column("描述", width=150)
        self.points_tree.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # 点操作按钮
        btn_frame = ttk.Frame(left_frame)
        btn_frame.pack(fill=tk.X)

        ttk.Button(btn_frame, text="添加点", command=self.add_point).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="编辑点", command=self.edit_point).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="删除点", command=self.delete_point).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="上移", command=self.move_up).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="下移", command=self.move_down).pack(side=tk.LEFT, padx=2)

        # 右侧：控制面板
        right_frame = ttk.LabelFrame(main_frame, text="控制面板", padding=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y)

        # 循环设置
        cycle_frame = ttk.LabelFrame(right_frame, text="循环设置", padding=5)
        cycle_frame.pack(fill=tk.X, pady=5)

        ttk.Label(cycle_frame, text="循环次数:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.cycle_var = tk.StringVar(value="1")
        ttk.Entry(cycle_frame, textvariable=self.cycle_var, width=10).grid(row=0, column=1, padx=5, pady=2)
        ttk.Label(cycle_frame, text="(0=无限循环)").grid(row=0, column=2, padx=5, pady=2)

        # 起点设置
        ttk.Label(cycle_frame, text="起点索引:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.start_var = tk.StringVar(value="0")
        ttk.Entry(cycle_frame, textvariable=self.start_var, width=10).grid(row=1, column=1, padx=5, pady=2)

        # 终点设置
        ttk.Label(cycle_frame, text="终点索引:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        self.end_var = tk.StringVar(value="0")
        ttk.Entry(cycle_frame, textvariable=self.end_var, width=10).grid(row=2, column=1, padx=5, pady=2)

        # 控制按钮
        control_frame = ttk.Frame(right_frame)
        control_frame.pack(fill=tk.X, pady=10)

        self.start_btn = ttk.Button(control_frame, text="启动循环", command=self.start_loop, width=15)
        self.start_btn.pack(pady=5)

        self.stop_btn = ttk.Button(control_frame, text="停止循环", command=self.stop_loop, state=tk.DISABLED, width=15)
        self.stop_btn.pack(pady=5)

        # 状态信息
        status_frame = ttk.LabelFrame(right_frame, text="状态信息", padding=5)
        status_frame.pack(fill=tk.X, pady=5)

        self.status_label = ttk.Label(status_frame, text="状态: 待机")
        self.status_label.pack(anchor=tk.W, pady=2)

        self.cycle_label = ttk.Label(status_frame, text="循环次数: 0/0")
        self.cycle_label.pack(anchor=tk.W, pady=2)

        self.current_action_label = ttk.Label(status_frame, text="当前动作: 无")
        self.current_action_label.pack(anchor=tk.W, pady=2)

        self.current_point_label = ttk.Label(status_frame, text="当前坐标点: 无")
        self.current_point_label.pack(anchor=tk.W, pady=2)

    def new_config(self):
        """新建配置"""
        if messagebox.askyesno("确认", "确定要新建配置吗？未保存的更改将丢失。"):
            self.route_points = []
            self.cycle_var.set("1")
            self.start_var.set("0")
            self.end_var.set("0")
            self.update_points_tree()
            self.config_file = "mc_route_config.json"

    def open_config(self):
        """打开配置文件"""
        file_path = filedialog.askopenfilename(
            title="打开配置文件",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
        )

        if file_path:
            self.load_config(file_path)

    def save_config(self):
        """保存配置文件"""
        if self.config_file and os.path.exists(self.config_file):
            self.save_config_to_file(self.config_file)
        else:
            self.save_config_as()

    def save_config_as(self):
        """另存为配置文件"""
        file_path = filedialog.asksaveasfilename(
            title="保存配置文件",
            defaultextension=".json",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
        )

        if file_path:
            self.save_config_to_file(file_path)
            self.config_file = file_path

    def save_config_to_file(self, file_path):
        """保存配置到文件"""
        try:
            config_data = {
                "cycle_count": self.cycle_var.get(),
                "start_index": self.start_var.get(),
                "end_index": self.end_var.get(),
                "route_points": self.route_points
            }

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, ensure_ascii=False, indent=2)

            messagebox.showinfo("成功", f"配置已保存到 {file_path}")
        except Exception as e:
            messagebox.showerror("错误", f"保存配置失败: {str(e)}")

    def load_config(self, file_path):
        """从文件加载配置"""
        if not os.path.exists(file_path):
            return False

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)

            # 加载循环设置
            self.cycle_var.set(config_data.get("cycle_count", "1"))
            self.start_var.set(config_data.get("start_index", "0"))
            self.end_var.set(config_data.get("end_index", "0"))

            # 加载路线点
            self.route_points = config_data.get("route_points", [])
            self.update_points_tree()

            self.config_file = file_path
            return True
        except Exception as e:
            messagebox.showerror("错误", f"加载配置失败: {str(e)}")
            return False

    def add_example_points(self):
        """添加示例路线点"""
        example_points = [
            {"coords": "637 177 -1139", "delay": 0, "desc": "起点"},
            {"coords": "470 190 -1013", "delay": 30, "desc": "矿洞入口"},
            {"coords": "353 236 -1014", "delay": 24, "desc": "BOSS刷新点"},
            {"coords": "637 177 -1139", "delay": 60, "desc": "返回起点"}
        ]

        for point in example_points:
            self.route_points.append(point)
            self.update_points_tree()

    def update_points_tree(self):
        """更新路线点列表显示"""
        # 清空现有列表
        for item in self.points_tree.get_children():
            self.points_tree.delete(item)

        # 添加新点
        for idx, point in enumerate(self.route_points):
            self.points_tree.insert("", "end", values=(
                idx,
                point["coords"],
                point["delay"],
                point["desc"]
            ))

    def add_point(self):
        """添加新路线点"""
        dialog = PointDialog(self.root, "添加路线点")
        if dialog.result:
            self.route_points.append(dialog.result)
            self.update_points_tree()

    def edit_point(self):
        """编辑选中的路线点"""
        selected = self.points_tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择一个路线点")
            return

        index = int(self.points_tree.item(selected[0], "values")[0])
        point = self.route_points[index]

        dialog = PointDialog(
            self.root,
            "编辑路线点",
            coords=point["coords"],
            delay=point["delay"],
            desc=point["desc"]
        )

        if dialog.result:
            self.route_points[index] = dialog.result
            self.update_points_tree()

    def delete_point(self):
        """删除选中的路线点"""
        selected = self.points_tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择一个路线点")
            return

        index = int(self.points_tree.item(selected[0], "values")[0])
        self.route_points.pop(index)
        self.update_points_tree()

    def move_up(self):
        """上移选中的路线点"""
        selected = self.points_tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择一个路线点")
            return

        index = int(self.points_tree.item(selected[0], "values")[0])
        if index > 0:
            # 交换位置
            self.route_points[index], self.route_points[index - 1] = self.route_points[index - 1], self.route_points[
                index]
            self.update_points_tree()
            # 重新选中移动后的点
            self.points_tree.selection_set(self.points_tree.get_children()[index - 1])

    def move_down(self):
        """下移选中的路线点"""
        selected = self.points_tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择一个路线点")
            return

        index = int(self.points_tree.item(selected[0], "values")[0])
        if index < len(self.route_points) - 1:
            # 交换位置
            self.route_points[index], self.route_points[index + 1] = self.route_points[index + 1], self.route_points[
                index]
            self.update_points_tree()
            # 重新选中移动后的点
            self.points_tree.selection_set(self.points_tree.get_children()[index + 1])

    def show_safety_warning(self):
        """显示安全警告"""
        message = (
            "MC自动寻路脚本 - 使用说明\n\n"
            "1. 确保游戏窗口处于前台（建议窗口化模式）\n"
            "2. 游戏分辨率建议设置为1920x1080\n"
            "3. 按F3+G显示区块边界辅助定位\n"
            "4. 快速停止：将鼠标拖动到屏幕左上角\n"
            "5. 使用Baritone模组的.b goto指令进行寻路\n"
            "6. 程序启动时会自动尝试加载 mc_route_config.json 路径配置文件,如果文件不存在，则加载默认示例点"
        )
        messagebox.showinfo("使用说明", message)

    def update_status(self, message):
        """更新状态标签"""
        self.status_label.config(text=f"状态: {message}")
        self.root.update()

    def update_current_action(self, action):
        """更新当前动作显示"""
        self.current_action_label.config(text=f"当前动作: {action}")
        self.root.update()

    def update_cycle_count(self):
        """更新循环次数显示"""
        total = "∞" if self.total_cycles == 0 else self.total_cycles
        self.cycle_label.config(text=f"循环次数: {self.cycle_count}/{total}")
        self.root.update()

    def update_current_point(self, point):
        """更新当前坐标点显示"""
        self.current_point_label.config(text=f"当前坐标点: {point}")
        self.root.update()

    def send_command(self, coords):
        """发送命令函数"""
        try:
            self.update_current_action(f"输入指令: .b goto {coords}")
            pyautogui.click(x=960, y=540)  # 确保游戏窗口激活
            pyautogui.press('t')  # 打开聊天框
            time.sleep(1.5)
            pyautogui.write(f".b goto {coords}", interval=0.1)  # 输入指令
            time.sleep(0.3)
            pyautogui.press('enter')  # 发送指令
            time.sleep(0.5)
        except Exception as e:
            self.update_status(f"输入失败: {str(e)}")

    def check_mouse_position(self):
        """检查鼠标是否在屏幕左上角附近"""
        try:
            x, y = pyautogui.position()
            # 如果鼠标在左上角10像素范围内，则停止程序
            if x < 10 and y < 10:
                return True
        except:
            pass
        return False

    def execute_sequence(self):
        """执行坐标序列操作"""
        try:
            self.update_status("启动中...")
            time.sleep(3)  # 给用户切换窗口的时间

            # 获取起点和终点索引
            start_idx = max(0, min(len(self.route_points) - 1, int(self.start_var.get())))
            end_idx = max(0, min(len(self.route_points) - 1, int(self.end_var.get())))

            # 确保终点索引不小于起点索引
            if end_idx < start_idx:
                start_idx, end_idx = end_idx, start_idx

            # 获取循环次数
            try:
                self.total_cycles = int(self.cycle_var.get())
            except:
                self.total_cycles = 1

            self.cycle_count = 0
            self.update_cycle_count()

            while self.is_running and (self.total_cycles == 0 or self.cycle_count < self.total_cycles):
                self.cycle_count += 1
                self.update_cycle_count()
                self.update_status(f"第 {self.cycle_count} 次循环")

                # 执行选定范围内的点
                for i in range(start_idx, end_idx + 1):
                    if not self.is_running:
                        break

                    # 检查鼠标位置以快速停止
                    if self.check_mouse_position():
                        self.is_running = False
                        break

                    point = self.route_points[i]
                    self.update_current_point(point["desc"])
                    self.send_command(point["coords"])
                    self.update_status(f"前往: {point['desc']}")

                    # 等待该点设置的延迟时间
                    total_wait = point["delay"]
                    if total_wait > 0:
                        for remaining in range(total_wait, 0, -1):
                            if not self.is_running:
                                break
                            if self.check_mouse_position():
                                self.is_running = False
                                break
                            self.update_current_action(f"{point['desc']} - 等待: {remaining}s")
                            time.sleep(1)

            self.update_status("已停止")
        except Exception as e:
            self.update_status(f"错误: {str(e)}")
        finally:
            self.is_running = False
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
            self.update_current_action("无")
            self.update_current_point("无")

    def start_loop(self):
        """启动循环线程"""
        if not self.route_points:
            messagebox.showwarning("警告", "请先添加路线点")
            return

        if not self.is_running:
            self.is_running = True
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            threading.Thread(target=self.execute_sequence, daemon=True).start()

    def stop_loop(self):
        """停止循环"""
        self.is_running = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.update_status("正在停止...")


class PointDialog(simpledialog.Dialog):
    """自定义点编辑对话框"""

    def __init__(self, parent, title, coords="", delay=0, desc=""):
        self.coords = coords
        self.delay = delay
        self.desc = desc
        self.result = None
        super().__init__(parent, title)

    def body(self, master):
        ttk.Label(master, text="坐标 (x y z):").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.coords_entry = ttk.Entry(master, width=20)
        self.coords_entry.grid(row=0, column=1, padx=5, pady=5)
        self.coords_entry.insert(0, self.coords)

        ttk.Label(master, text="等待时间 (秒):").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.delay_entry = ttk.Entry(master, width=10)
        self.delay_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        self.delay_entry.insert(0, str(self.delay))

        ttk.Label(master, text="描述:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.desc_entry = ttk.Entry(master, width=20)
        self.desc_entry.grid(row=2, column=1, padx=5, pady=5)
        self.desc_entry.insert(0, self.desc)

        return self.coords_entry  # 初始焦点

    def validate(self):
        try:
            # 验证坐标格式
            coords = self.coords_entry.get()
            parts = coords.split()
            if len(parts) != 3:
                raise ValueError("坐标格式错误")

            # 验证等待时间
            delay = int(self.delay_entry.get())
            if delay < 0:
                raise ValueError("等待时间不能为负数")

            self.result = {
                "coords": coords,
                "delay": delay,
                "desc": self.desc_entry.get()
            }
            return True
        except Exception as e:
            messagebox.showerror("输入错误", str(e))
            return False


if __name__ == "__main__":
    root = tk.Tk()
    app = MinecraftAutoGotoApp(root)
    root.mainloop()
