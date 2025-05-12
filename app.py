import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import networkx as nx
import re
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import graphviz
import random
from collections import defaultdict
random.seed(42)


class TextGraphApp:
    def __init__(self, root):
        self.root = root
        self.root.title("文本图结构分析")
        self.root.geometry("1200x800")  # 增加窗口大小以适应图形展示
        
        # 存储图结构
        self.graph = None
        
        # 创建界面组件
        self.create_widgets()
        self.create_bridge_words_ui()
        self.create_new_text_processing_ui()
        self.create_shortest_path_ui()
        self.create_pagerank_ui()

    def create_widgets(self):
        # 顶部控制区域
        top_frame = tk.Frame(self.root)
        top_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # 文件选择按钮
        self.file_btn = tk.Button(top_frame, text="选择文本文件", command=self.load_file)
        self.file_btn.pack(side=tk.LEFT, padx=5)
        
        # 显示所选文件路径
        self.file_path_var = tk.StringVar()
        self.file_path_var.set("未选择文件")
        file_path_label = tk.Label(top_frame, textvariable=self.file_path_var)
        file_path_label.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # 生成图结构按钮
        self.generate_btn = tk.Button(top_frame, text="生成图结构", command=self.generate_graph, state=tk.DISABLED)
        self.generate_btn.pack(side=tk.RIGHT, padx=5)
        
        # 创建内容显示区域
        content_frame = tk.Frame(self.root)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 左侧：原始文本和图结构信息
        left_frame = tk.Frame(content_frame, width=380)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # 文本显示区域
        text_label = tk.Label(left_frame, text="文本内容:")
        text_label.pack(anchor=tk.W)
        
        self.text_display = scrolledtext.ScrolledText(left_frame, wrap=tk.WORD, height=10)
        self.text_display.pack(fill=tk.X, expand=True)
        
        # 图结构信息区域
        graph_info_label = tk.Label(left_frame, text="图结构信息:")
        graph_info_label.pack(anchor=tk.W, pady=(10, 0))
        
        self.graph_info = scrolledtext.ScrolledText(left_frame, wrap=tk.WORD, height=15)
        self.graph_info.pack(fill=tk.X, expand=True)
        
        # 右侧：图形展示区域
        right_frame = tk.Frame(content_frame, width=800)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # 图形展示控制区域
        graph_control_frame = tk.Frame(right_frame)
        graph_control_frame.pack(fill=tk.X, pady=(0, 5))
        
        # 图形布局选项
        layout_label = tk.Label(graph_control_frame, text="布局:")
        layout_label.pack(side=tk.LEFT, padx=5)
        
        self.layout_var = tk.StringVar(value="dot")
        layout_options = ["dot", "neato", "fdp", "sfdp", "twopi", "circo"]
        layout_menu = tk.OptionMenu(graph_control_frame, self.layout_var, *layout_options)
        layout_menu.pack(side=tk.LEFT, padx=5)
        
        # 刷新图形按钮
        refresh_btn = tk.Button(graph_control_frame, text="刷新图形", command=self.refresh_graph)
        refresh_btn.pack(side=tk.RIGHT, padx=5)
        
        # 图形展示区域
        self.graph_frame = tk.Frame(right_frame, bg='white')
        self.graph_frame.pack(fill=tk.BOTH, expand=True)
        
        # 底部状态栏
        self.status_var = tk.StringVar()
        self.status_var.set("准备就绪")
        status_bar = tk.Label(self.root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)


    def create_bridge_words_ui(self):
        """创建桥接词查询界面组件"""
        bridge_frame = tk.Frame(self.root)
        bridge_frame.pack(fill=tk.X, padx=10, pady=5)

        # 输入框和按钮
        input_frame = tk.Frame(bridge_frame)
        input_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(input_frame, text="Word1:").pack(side=tk.LEFT)
        self.word1_entry = tk.Entry(input_frame, width=20)
        self.word1_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Label(input_frame, text="Word2:").pack(side=tk.LEFT)
        self.word2_entry = tk.Entry(input_frame, width=20)
        self.word2_entry.pack(side=tk.LEFT, padx=5)
        
        self.bridge_btn = tk.Button(input_frame, text="查询桥接词", command=self.find_bridge_words, state=tk.DISABLED)
        self.bridge_btn.pack(side=tk.LEFT, padx=5)

        # 结果显示区域
        self.result_label = tk.Label(bridge_frame, text="", wraplength=1000, justify=tk.LEFT)
        self.result_label.pack(fill=tk.X, pady=5)


    def create_new_text_processing_ui(self):
        """创建新文本处理界面组件"""
        new_text_frame = tk.Frame(self.root)
        new_text_frame.pack(fill=tk.X, padx=10, pady=5)

        input_frame = tk.Frame(new_text_frame)
        input_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(input_frame, text="新文本:").pack(side=tk.LEFT)
        self.new_text_entry = tk.Entry(input_frame, width=50)
        self.new_text_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        self.process_text_btn = tk.Button(input_frame, text="处理文本", 
                                        command=self.process_new_text, state=tk.DISABLED)
        self.process_text_btn.pack(side=tk.LEFT, padx=5)

        self.processed_text_result = scrolledtext.ScrolledText(new_text_frame, 
                                                              wrap=tk.WORD, height=4)
        self.processed_text_result.pack(fill=tk.X, pady=5)


    def create_shortest_path_ui(self):
        """创建最短路径查询界面组件"""
        shortest_path_frame = tk.Frame(self.root)
        shortest_path_frame.pack(fill=tk.X, padx=10, pady=5)

        input_frame = tk.Frame(shortest_path_frame)
        input_frame.pack(fill=tk.X, pady=5)
        
        # 修改输入框标签说明
        tk.Label(input_frame, text="起点:").pack(side=tk.LEFT)
        self.start_word_entry = tk.Entry(input_frame, width=20)
        self.start_word_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Label(input_frame, text="终点（可选）:").pack(side=tk.LEFT)  # 修改标签说明
        self.end_word_entry = tk.Entry(input_frame, width=20)
        self.end_word_entry.pack(side=tk.LEFT, padx=5)
        
        self.shortest_path_btn = tk.Button(input_frame, text="计算路径", 
                                        command=self.calculate_shortest_path, 
                                        state=tk.DISABLED)
        self.shortest_path_btn.pack(side=tk.LEFT, padx=5)

        # 使用ScrolledText支持滚动查看
        self.shortest_path_result = scrolledtext.ScrolledText(shortest_path_frame,
                                                            wrap=tk.WORD,
                                                            height=8,
                                                            font=("Consolas", 10))
        self.shortest_path_result.pack(fill=tk.BOTH, expand=True, pady=5)

    def calculate_shortest_path(self):
        start = self.start_word_entry.get().lower().strip()
        end = self.end_word_entry.get().lower().strip()

        # 输入验证
        if not start:
            self.shortest_path_result.delete(1.0, tk.END)
            self.shortest_path_result.insert(tk.END, "错误：必须输入起点单词")
            return

        if not self.graph.has_node(start):
            self.shortest_path_result.delete(1.0, tk.END)
            self.shortest_path_result.insert(tk.END, f"错误：起点 '{start}' 不在图中")
            return

        # 单节点模式
        if not end:
            try:
                paths = nx.single_source_dijkstra_path(self.graph, start, weight='weight')
                lengths = nx.single_source_dijkstra_path_length(self.graph, start, weight='weight')
            except nx.NetworkXException as e:
                self.shortest_path_result.delete(1.0, tk.END)
                self.shortest_path_result.insert(tk.END, f"计算错误：{str(e)}")
                return

            # 格式化输出
            result = []
            for target in sorted(paths.keys()):
                if target == start:
                    continue
                    
                path = paths[target]
                length = lengths[target]
                result.append(f"{start} → {target}:")
                result.append(f"   路径: {' → '.join(path)}")
                result.append(f"   长度: {length}\n")
            
            # 处理不可达节点
            unreachable = sorted(set(self.graph.nodes()) - set(paths.keys()) - {start})
            if unreachable:
                result.append(f"\n不可达节点 ({len(unreachable)}):")
                result.append(", ".join(unreachable))
            
            self.shortest_path_result.delete(1.0, tk.END)
            self.shortest_path_result.insert(tk.END, "\n".join(result))
            self.shortest_paths = None
            self.refresh_graph()
            return

        # 原双节点模式（保持原有逻辑）
        if not self.graph.has_node(end):
            self.shortest_path_result.delete(1.0, tk.END)
            self.shortest_path_result.insert(tk.END, f"错误：终点 '{end}' 不在图中")
            return

        try:
            path_length = nx.dijkstra_path_length(self.graph, start, end, weight='weight')
            all_paths = list(nx.all_shortest_paths(self.graph, start, end, weight='weight'))
        except nx.NetworkXNoPath:
            self.shortest_path_result.delete(1.0, tk.END)
            self.shortest_path_result.insert(tk.END, f"{start} 到 {end} 不可达")
            self.shortest_paths = None
            self.refresh_graph()
            return

        self.shortest_paths = all_paths
        
        path_texts = []
        for idx, path in enumerate(all_paths, 1):
            path_str = " → ".join(path)
            path_texts.append(f"路径{idx}: {path_str} (长度: {path_length})")
        
        self.shortest_path_result.delete(1.0, tk.END)
        self.shortest_path_result.insert(tk.END, "\n".join(path_texts))
        self.refresh_graph()


    def find_bridge_words(self):
        """查找并显示桥接词"""
        word1 = self.word1_entry.get().lower()
        word2 = self.word2_entry.get().lower()

        # 检查单词是否存在
        if not self.graph.has_node(word1) or not self.graph.has_node(word2):
            missing = []
            if not self.graph.has_node(word1):
                missing.append(word1)
            if not self.graph.has_node(word2):
                missing.append(word2)
            self.result_label.config(text=f"No {' or '.join(missing)} in the graph!")
            return

        # 查找桥接词
        bridge_words = self.find_bridge_words_for_pair(word1, word2)

        # 生成结果文本
        if not bridge_words:
            result_text = f"No bridge words from {word1} to {word2}!"
        else:
            if len(bridge_words) == 1:
                result_text = f"The bridge words from {word1} to {word2} are: {bridge_words[0]}."
            else:
                formatted = ", ".join(bridge_words[:-1]) + f" and {bridge_words[-1]}"
                result_text = f"The bridge words from {word1} to {word2} are: {formatted}."
        
        self.result_label.config(text=result_text)


    def generate_graph(self):
        """根据文本生成有向图结构"""
        if not self.file_path_var.get() or self.file_path_var.get() == "未选择文件":
            messagebox.showwarning("警告", "请先选择文本文件")
            return
        
        # 获取文本内容
        text_content = self.text_display.get(1.0, tk.END)
        
        # 预处理文本
        words = self.preprocess_text(text_content)
        
        if len(words) < 2:
            messagebox.showwarning("警告", "文本内容太少，无法生成有效的图结构")
            self.status_var.set("文本内容不足")
            return

        # 创建有向图
        self.graph = nx.DiGraph()
        
        # 添加边和权重
        for i in range(len(words) - 1):
            word1 = words[i]
            word2 = words[i + 1]
            
            if self.graph.has_edge(word1, word2):
                self.graph[word1][word2]['weight'] += 1
            else:
                self.graph.add_edge(word1, word2, weight=1)
        
        # 显示图结构信息
        self.display_graph_info()
        
        # 生成并显示图形
        self.refresh_graph()
        
        self.status_var.set("图结构已生成")
        messagebox.showinfo("成功", "图结构已成功生成")

        self.bridge_btn.config(state=tk.NORMAL)
        self.process_text_btn.config(state=tk.NORMAL)
        self.shortest_path_btn.config(state=tk.NORMAL)
        self.pagerank_btn.config(state=tk.NORMAL)


    def refresh_graph(self):
        if not self.graph:
            return
        
        # 清除现有图形
        for widget in self.graph_frame.winfo_children():
            widget.destroy()
        
        # 创建新的图形
        dot = graphviz.Digraph(comment='Text Graph')
        dot.attr(rankdir='LR')  # 从左到右的布局
        
        # 添加节点
        if hasattr(self, 'pagerank') and self.pagerank is not None:
            max_pr = max(self.pagerank.values()) or 1  # 防止除零
            for node in self.graph.nodes():
                pr = self.pagerank[node]
                normalized = pr / max_pr
                # 根据PR值设置节点大小和颜色
                dot.node(node, 
                        label=f"{node}\n{pr:.3f}",
                        width=str(0.5 + normalized * 2),
                        height=str(0.3 + normalized * 1),
                        style='filled',
                        fillcolor=f"{int(255*(1-normalized))},255,255")  # 颜色渐变
        else:
            for node in self.graph.nodes():
                dot.node(node)

        # 添加边
        edge_colors = defaultdict(list)
        if hasattr(self, 'shortest_paths') and self.shortest_paths is not None:
            colors = ['#FF0000', '#0000FF', '#00FF00', '#FFA500', '#800080']
            for path_idx, path in enumerate(self.shortest_paths):
                color = colors[path_idx % len(colors)]
                for i in range(len(path)-1):
                    edge = (path[i], path[i+1])
                    edge_colors[edge].append(color)
        
        for u, v, data in self.graph.edges(data=True):
            edge = (u, v)
            if edge in edge_colors:
                color_str = ":".join(edge_colors[edge])
                dot.edge(u, v, label=str(data['weight']), 
                        color=color_str, penwidth='2.5', style='bold')
            else:
                dot.edge(u, v, label=str(data['weight']))

        
        # 设置布局引擎
        dot.engine = self.layout_var.get()
        
        # 渲染图形
        try:
            # 保存图形文件
            dot.render('temp_graph', format='png', cleanup=True)
            
            # 加载并显示图形
            img = tk.PhotoImage(file='temp_graph.png')
            img_label = tk.Label(self.graph_frame, image=img)
            img_label.image = img  # 保持引用
            img_label.pack(fill=tk.BOTH, expand=True)
            
            self.status_var.set("图形已更新")
        except Exception as e:
            messagebox.showerror("错误", f"无法生成图形: {str(e)}")
            self.status_var.set("图形生成失败")

    def load_file(self):
        """选择并加载文本文件"""
        file_path = filedialog.askopenfilename(
            title="选择文本文件",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        
        if file_path:
            self.file_path_var.set(file_path)
            self.generate_btn.config(state=tk.NORMAL)

            # 显示文件内容
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.text_display.delete(1.0, tk.END)
                    self.text_display.insert(tk.END, content)
                self.status_var.set(f"已加载文件: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("错误", f"无法读取文件: {str(e)}")
                self.status_var.set("文件加载失败")
    
    def preprocess_text(self, text):
        """预处理文本，提取单词"""
        # 将文本转为小写并替换标点符号为空格
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        # 分割为单词列表
        words = text.split()
        return words
 

    def process_new_text(self):
        new_text = self.new_text_entry.get()
        original_words = new_text.split()
        processed_words = []

        for i in range(len(original_words)):
            processed_words.append(original_words[i])  # 保持原格式
            
            if i < len(original_words) - 1:
                word1 = original_words[i].lower()
                word2 = original_words[i+1].lower()
                
                bridge_words = self.find_bridge_words_for_pair(word1, word2)
                
                if bridge_words:
                    selected = random.choice(bridge_words)
                    processed_words.append(selected)
        
        new_text = ' '.join(processed_words)
        self.processed_text_result.delete(1.0, tk.END)
        self.processed_text_result.insert(tk.END, new_text)

    def find_bridge_words_for_pair(self, word1, word2):
        if not self.graph.has_node(word1) or not self.graph.has_node(word2):
            return []
        
        bridges = []
        for successor in self.graph.successors(word1):
            if self.graph.has_edge(successor, word2):
                bridges.append(successor)
        return bridges


    def display_graph_info(self):
        """显示图结构的基本信息"""
        if not self.graph:
            return
        
        self.graph_info.delete(1.0, tk.END)
        
        info_text = "图结构信息:\n\n"
        info_text += f"节点数量: {self.graph.number_of_nodes()}\n"
        info_text += f"边数量: {self.graph.number_of_edges()}\n\n"
        
        info_text += "节点列表:\n"
        for node in sorted(self.graph.nodes()):
            info_text += f"- {node}\n"
        
        info_text += "\n边列表 (源节点 -> 目标节点: 权重):\n"
        for u, v, data in sorted(self.graph.edges(data=True)):
            info_text += f"- {u} -> {v}: {data['weight']}\n"
        
        self.graph_info.insert(tk.END, info_text)


    def create_pagerank_ui(self):
        """创建PageRank计算界面组件"""
        pagerank_frame = tk.Frame(self.root)
        pagerank_frame.pack(fill=tk.X, padx=10, pady=5)

        input_frame = tk.Frame(pagerank_frame)
        input_frame.pack(fill=tk.X, pady=5)

        tk.Label(input_frame, text="阻尼因子d (0-1):").pack(side=tk.LEFT)
        self.d_entry = tk.Entry(input_frame, width=10)
        self.d_entry.insert(0, "0.85")  # 设置默认值
        self.d_entry.pack(side=tk.LEFT, padx=5)

        self.pagerank_btn = tk.Button(input_frame, text="计算PageRank", 
                                    command=self.calculate_pagerank, state=tk.DISABLED)
        self.pagerank_btn.pack(side=tk.LEFT, padx=5)

        self.pagerank_result = scrolledtext.ScrolledText(pagerank_frame, 
                                                        wrap=tk.WORD, height=6)
        self.pagerank_result.pack(fill=tk.BOTH, expand=True, pady=5)


    def calculate_pagerank(self):
        """计算并展示PageRank值"""
        # 获取并验证阻尼因子
        try:
            d = float(self.d_entry.get())
            if not 0 <= d <= 1:
                raise ValueError
        except:
            messagebox.showerror("错误", "请输入0到1之间的有效阻尼因子")
            return

        # 检查图是否存在
        if not self.graph or len(self.graph.nodes()) == 0:
            messagebox.showwarning("警告", "请先生成图结构")
            return

        # 初始化参数
        nodes = list(self.graph.nodes())
        N = len(nodes)
        pr = {node: 1/N for node in nodes}
        iterations = 100
        epsilon = 1e-6

        # PageRank迭代计算
        for _ in range(iterations):
            new_pr = {}
            max_diff = 0
            for u in nodes:
                # 计算所有前驱节点的贡献
                sum_contribution = 0
                for v in self.graph.predecessors(u):
                    L_v = self.graph.out_degree(v)  # 出度边的数量
                    if L_v == 0:
                        sum_contribution += pr[v] / N  # 处理悬挂节点
                    else:
                        sum_contribution += pr[v] / L_v
                new_pr[u] = (1-d)/N + d * sum_contribution
                max_diff = max(max_diff, abs(new_pr[u] - pr[u]))
            pr = new_pr
            if max_diff < epsilon:
                break

        # 存储结果并展示
        self.pagerank = pr
        sorted_pr = sorted(pr.items(), key=lambda x: x[1], reverse=True)
        
        # 显示文本结果
        result_text = "PageRank值（从高到低）:\n\n"
        for node, value in sorted_pr:
            result_text += f"{node}: {value:.6f}\n"
        self.pagerank_result.delete(1.0, tk.END)
        self.pagerank_result.insert(tk.END, result_text)

        # 更新图形展示
        self.refresh_graph()


if __name__ == "__main__":
    root = tk.Tk()
    app = TextGraphApp(root)
    root.mainloop()
