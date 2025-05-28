import re
import random
from collections import defaultdict
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import threading
import graphviz
random.seed(42)

class GraphApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Graph Processing Tool")
        self.graph = defaultdict(lambda: defaultdict(int))
        self.reverse_graph = defaultdict(list)
        self.nodes = []
        self.out_degree = {}
        self.pr_values = {}

        # 新增图形控制变量
        self.img_scale = 1.0
        self.img_offset_x = 0
        self.img_offset_y = 0
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.current_image = None
        self.auto_render = True  # 新增渲染状态标志
        self.pending_render = False  # 新增待渲染标记

        # GUI布局
        self.create_widgets()

    def create_widgets(self):
        # 文件选择部分
        self.file_frame = ttk.Frame(self.root)
        self.file_frame.pack(pady=5)
        self.file_btn = ttk.Button(
            self.file_frame, text="选择文件", command=self.load_file)
        self.file_btn.pack(side=tk.LEFT)
        self.file_label = ttk.Label(self.file_frame, text="未选择文件")
        self.file_label.pack(side=tk.LEFT, padx=5)

        # 渲染控制按钮
        self.render_btn = ttk.Button(
            self.file_frame, 
            text="自动渲染: ON", 
            command=self.toggle_render
        )
        self.render_btn.pack(side=tk.LEFT, padx=10)

        self.manual_render_btn = ttk.Button(
            self.file_frame,
            text="立即渲染",
            command=self.force_render,
            state=tk.DISABLED
        )
        self.manual_render_btn.pack(side=tk.LEFT)

        # 图显示区域
        self.graph_frame = ttk.Frame(self.root)
        self.graph_frame.pack(pady=5)
        self.canvas = tk.Canvas(self.graph_frame, width=800, height=600)
        self.canvas.pack()

        # 绑定画布事件
        self.canvas.bind("<ButtonPress-1>", self.start_drag)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<MouseWheel>", self.on_zoom)
        
        # 功能选项卡
        self.notebook = ttk.Notebook(self.root)
        
        # 桥接词查询
        self.bridge_tab = ttk.Frame(self.notebook)
        self.create_bridge_widgets()
        
        # 新文本处理
        self.newtext_tab = ttk.Frame(self.notebook)
        self.create_newtext_widgets()
        
        # 最短路径
        self.shortest_tab = ttk.Frame(self.notebook)
        self.create_shortest_widgets()
        
        # PageRank
        self.pagerank_tab = ttk.Frame(self.notebook)
        self.create_pagerank_widgets()

        self.traversal_tab = ttk.Frame(self.notebook)
        self.create_traversal_widgets()

        self.notebook.add(self.bridge_tab, text="桥接词")
        self.notebook.add(self.newtext_tab, text="文本扩展")
        self.notebook.add(self.shortest_tab, text="最短路径")
        self.notebook.add(self.pagerank_tab, text="PageRank")
        self.notebook.add(self.traversal_tab, text="随机遍历")
        self.notebook.pack(expand=True, fill=tk.BOTH)

    def toggle_render(self):
        """切换渲染模式"""
        self.auto_render = not self.auto_render
        btn_text = "自动渲染: ON" if self.auto_render else "自动渲染: OFF"
        self.render_btn.config(text=btn_text)
        
        # 控制手动渲染按钮状态
        self.manual_render_btn.config(
            state=tk.NORMAL if not self.auto_render else tk.DISABLED
        )
        
        # 如果切换回自动模式且有未渲染的更新
        if self.auto_render and self.pending_render:
            self.show_graph()
            self.pending_render = False

    def force_render(self):
        """手动触发渲染"""
        if self.pending_render:
            self.show_graph()
            self.pending_render = False

    def create_bridge_widgets(self):
        ttk.Label(self.bridge_tab, text="单词1:").grid(row=0, column=0, padx=5, pady=5)
        self.word1_entry = ttk.Entry(self.bridge_tab)
        self.word1_entry.grid(row=0, column=1)
        
        ttk.Label(self.bridge_tab, text="单词2:").grid(row=1, column=0, padx=5, pady=5)
        self.word2_entry = ttk.Entry(self.bridge_tab)
        self.word2_entry.grid(row=1, column=1)
        
        ttk.Button(self.bridge_tab, text="查询桥接词", command=self.find_bridge).grid(row=2, column=0, columnspan=2)
        self.bridge_result = ttk.Label(self.bridge_tab, text="")
        self.bridge_result.grid(row=3, column=0, columnspan=2)

    def create_newtext_widgets(self):
        ttk.Label(self.newtext_tab, text="输入新文本:").pack(pady=5)
        self.newtext_entry = ttk.Entry(self.newtext_tab, width=50)
        self.newtext_entry.pack()
        ttk.Button(self.newtext_tab, text="处理文本", command=self.process_text).pack(pady=5)
        self.newtext_result = ttk.Label(self.newtext_tab, text="")
        self.newtext_result.pack()

    def create_shortest_widgets(self):
        ttk.Label(self.shortest_tab, text="起点:").grid(row=0, column=0, padx=5, pady=5)
        self.start_entry = ttk.Entry(self.shortest_tab)
        self.start_entry.grid(row=0, column=1)
        
        ttk.Label(self.shortest_tab, text="终点:").grid(row=1, column=0, padx=5, pady=5)
        self.end_entry = ttk.Entry(self.shortest_tab)
        self.end_entry.grid(row=1, column=1)
        
        ttk.Button(self.shortest_tab, text="查找路径", command=self.find_shortest).grid(row=2, column=0, columnspan=2)
        self.shortest_result = ttk.Label(self.shortest_tab, text="")
        self.shortest_result.grid(row=3, column=0, columnspan=2)

    def create_pagerank_widgets(self):
        ttk.Button(self.pagerank_tab, text="计算PageRank", command=self.compute_pagerank).pack(pady=5)
        self.pagerank_text = tk.Text(self.pagerank_tab, height=10, width=50)
        self.pagerank_text.pack()

    def create_traversal_widgets(self):
        self.traversal_running = False
        self.stop_event = None
        self.traversal_path = []

        control_frame = ttk.Frame(self.traversal_tab)
        control_frame.pack(pady=10)
        
        self.start_btn = ttk.Button(
            control_frame, 
            text="开始遍历",
            command=self.start_traversal
        )
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(
            control_frame,
            text="停止遍历",
            command=self.stop_traversal,
            state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        # 路径显示区域
        self.path_text = tk.Text(self.traversal_tab, height=15, width=80)
        self.path_text.pack(pady=5)
        
        # 保存按钮
        ttk.Button(
            self.traversal_tab,
            text="保存结果",
            command=self.save_traversal
        ).pack(pady=5)

    def start_traversal(self):
        if not self.graph:
            messagebox.showwarning("警告", "请先加载图数据")
            return
        
        self.traversal_running = True
        self.stop_event = threading.Event()
        self.traversal_path.clear()
        self.path_text.delete(1.0, tk.END)
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        
        # 创建后台线程
        threading.Thread(target=self.run_traversal).start()

    def run_traversal(self):
        # 随机选择起始节点
        current = random.choice(list(self.graph.keys()))
        visited_edges = set()
        
        while self.traversal_running:
            self.traversal_path.append(current)
            self.update_path_display(current)
            
            # 获取当前节点的出边
            neighbors = list(self.graph[current].items())
            if not neighbors:
                break
                
            # 随机选择下一条边
            next_node, weight = random.choice(neighbors)
            edge = (current, next_node)
            
            # 检查重复边
            if edge in visited_edges:
                self.traversal_path.append(f"重复边: {edge}")
                break
                
            visited_edges.add(edge)
            current = next_node
            
            # 检查停止事件
            if self.stop_event.wait(0.1):
                break
                
        self.traversal_running = False
        self.root.after(0, self.end_traversal)

    def update_path_display(self, node):
        self.root.after(0, lambda: self.path_text.insert(
            tk.END, f"当前节点: {node}\n"))
        self.root.after(0, self.path_text.see, tk.END)

    def stop_traversal(self):
        if self.traversal_running:
            self.stop_event.set()
            self.traversal_running = False

    def end_traversal(self):
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.path_text.insert(tk.END, "\n遍历结束\n")
        
    def save_traversal(self):
        if not self.traversal_path:
            messagebox.showwarning("警告", "没有可保存的遍历路径")
            return
            
        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")]
        )
        if filepath:
            with open(filepath, 'w') as f:
                f.write("遍历路径记录:\n")
                for step in self.traversal_path:
                    if isinstance(step, tuple):
                        f.write(f"经过边: {step[0]} -> {step[1]}\n")
                    else:
                        f.write(f"到达节点: {step}\n")
            messagebox.showinfo("保存成功", f"文件已保存至: {filepath}")

    def load_file(self):
        filepath = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if filepath:
            self.file_label.config(text=filepath)
            with open(filepath, 'r', encoding='utf8') as f:
                text = f.read().lower()
            self.build_graph(text)
            self.show_graph()

    def build_graph(self, text):
        self.graph.clear()
        self.reverse_graph.clear()
        words = re.findall(r'\b\w+\b', text)
        nodes = set()
        for i in range(len(words)-1):
            u, v = words[i], words[i+1]
            self.graph[u][v] += 1  # 记录u到v的边权重
            self.reverse_graph[v].append(u)
            nodes.add(u)
            nodes.add(v)
        self.nodes = list(nodes)
        self.out_degree = {u: sum(v.values()) for u, v in self.graph.items()}

    def show_graph(self):
        if not self.auto_render:
            self.pending_render = True
            return

        dot = graphviz.Digraph()
        for u in self.graph:
            dot.node(u)
            for v, w in self.graph[u].items():
                dot.edge(u, v, label=str(w))
        dot.render('graph', format='png', cleanup=True)
        img = Image.open('graph.png')
        # img = img.resize((800, 600), Image.Resampling.LANCZOS)
        self.img_tk = ImageTk.PhotoImage(img)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.img_tk)

    def find_bridge(self):
        word1 = self.word1_entry.get().lower()
        word2 = self.word2_entry.get().lower()
        
        if word1 not in self.graph or word2 not in self.graph:
            self.bridge_result.config(text=f"No {word1} or {word2} in the graph!")
            return
        
        bridges = []
        for word3 in self.graph.get(word1, {}):
            if word2 in self.graph.get(word3, {}):
                bridges.append(word3)
        
        if not bridges:
            self.bridge_result.config(text=f"No bridge words from {word1} to {word2}!")
        else:
            bridges_str = ', '.join(bridges[:-1]) + f" and {bridges[-1]}" if len(bridges) > 1 else bridges[0]
            self.bridge_result.config(text=f"The bridge words from {word1} to {word2} are: {bridges_str}")

    def process_text(self):
        new_text = self.newtext_entry.get().lower()
        words = re.findall(r'\b\w+\b', new_text)
        if len(words) < 2:
            self.newtext_result.config(text=new_text)
            return
        
        result = []
        for i in range(len(words)-1):
            a = words[i].lower()
            b = words[i+1].lower()
            result.append(words[i])
            
            if a in self.graph and b in self.graph:
                bridges = []
                for word3 in self.graph.get(a, {}):
                    if b in self.graph.get(word3, {}):
                        bridges.append(word3)
                if bridges:
                    bridge = random.choice(bridges)
                    result.append(bridge)
        
        result.append(words[-1])
        self.newtext_result.config(text=' '.join(result))

    def find_shortest(self):
        start = self.start_entry.get().lower()
        end = self.end_entry.get().lower()
        
        if start not in self.graph or end not in self.graph:
            messagebox.showerror("错误", "单词不存在于图中")
            return
        
        # 实现Dijkstra算法
        distances = {node: float('inf') for node in self.nodes}
        distances[start] = 0
        predecessors = defaultdict(list)
        visited = set()
        
        while len(visited) < len(self.nodes):
            current = min(
                (node for node in self.nodes if node not in visited), 
                key=lambda x: distances[x]
            )
            visited.add(current)
            
            for neighbor, weight in self.graph[current].items():
                if distances[current] + weight < distances[neighbor]:
                    distances[neighbor] = distances[current] + weight
                    predecessors[neighbor] = [current]
                elif distances[current] + weight == distances[neighbor]:
                    predecessors[neighbor].append(current)
        
        if distances[end] == float('inf'):
            self.shortest_result.config(text="不可达")
            return
        
        # 收集所有路径
        paths = []
        def collect_paths(node, path):
            if node == start:
                paths.append([start] + path)
            else:
                for pred in predecessors[node]:
                    collect_paths(pred, [node] + path)
        
        collect_paths(end, [])
        paths = [p for p in paths]
        
        if self.auto_render:
            self.highlight_path(paths)
        else:
            self.pending_render = True

        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.img_tk)
        self.shortest_result.config(text=f"最短路径长度: {distances[end]}\n路径: {' -> '.join(paths[0])}")

    def render_and_show(self, dot):
        """通用渲染显示方法"""
        dot.render('temp_graph', format='png', cleanup=True)
        img = Image.open('temp_graph.png')
        # img = img.resize((800, 600), Image.Resampling.LANCZOS)
        self.img_tk = ImageTk.PhotoImage(img)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.img_tk)

    def highlight_path(self, paths):
        """独立出来的路径高亮渲染方法"""
        # 高亮显示路径
        dot = graphviz.Digraph()
        for u in self.graph:
            dot.node(u)
            for v, w in self.graph[u].items():
                dot.edge(u, v, label=str(w))
        
        edges = set()
        colors = ['blue', 'yellow', 'green', 'purple', 'pink']
        for c, path in enumerate(paths):
            for i in range(len(path)-1):
                if (path[i], path[i+1]) not in edges:
                    dot.edge(path[i], path[i+1], color=colors[c % len(colors)], penwidth='2')
                    edges.add((path[i], path[i+1]))
 
        # 添加渲染控制
        if self.auto_render:
            self.render_and_show(dot)

    def start_drag(self, event):
        self.drag_start_x = event.x
        self.drag_start_y = event.y

    def on_drag(self, event):
        delta_x = event.x - self.drag_start_x
        delta_y = event.y - self.drag_start_y
        self.canvas.move("all", delta_x, delta_y)
        self.drag_start_x = event.x
        self.drag_start_y = event.y

    def on_zoom(self, event):
        scale_factor = 1.1 if event.delta > 0 else 0.9
        self.img_scale *= scale_factor
        
        # 获取当前画布中心
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        
        # 缩放图形
        self.canvas.scale("all", x, y, scale_factor, scale_factor)

    def compute_pagerank(self):
        d = 0.85
        max_iter = 100
        tol = 1e-6
        N = len(self.nodes)
        
        if N == 0:
            return
        
        pr = {node: 1.0/N for node in self.nodes}
        
        for _ in range(max_iter):
            new_pr = {}
            # 计算所有出度为0节点的总贡献
            zero_out_pr = sum(pr[node] for node in self.nodes if self.out_degree.get(node, 0) == 0)
            common_contribution = (zero_out_pr / N) * d if N > 0 else 0
            
            for node in self.nodes:
                # 正常入链贡献
                incoming = sum(pr[v]/self.out_degree[v] for v in self.reverse_graph.get(node, []) if self.out_degree[v] > 0)
                
                new_pr[node] = (1-d)/N + d * incoming + common_contribution
            
            # 检查收敛
            if sum(abs(new_pr[n] - pr[n]) for n in self.nodes) < tol:
                break
            pr = new_pr
        
        sorted_pr = sorted(pr.items(), key=lambda x: x[1], reverse=True)
        self.pagerank_text.delete(1.0, tk.END)
        for node, value in sorted_pr:
            self.pagerank_text.insert(tk.END, f"{node}: {value:.6f}\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = GraphApp(root)
    root.mainloop()
