#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高级文件清理工具 - wxPython GUI应用程序
功能：支持按后缀删除和无后缀文件清理，包含回收站功能和白名单保护
"""

import wx
import wx.adv
import os
import glob
import logging
import datetime
import shutil
from pathlib import Path
import send2trash  # 用于安全删除到回收站

class AdvancedFileCleanerApp(wx.Frame):
    """高级文件清理工具主应用程序窗口"""
    
    def __init__(self):
        super().__init__(None, title="高级文件清理工具", size=(900, 700))
        
        # 设置日志记录
        self.setup_logging()
        
        # 初始化变量
        self.selected_folder = ""
        self.files_to_delete = []
        self.whitelist_dirs = self.load_default_whitelist()
        self.whitelist_files = []
        
        # 创建界面
        self.create_ui()
        
        # 居中显示窗口
        self.Centre()
        
        # 绑定事件
        self.Bind(wx.EVT_CLOSE, self.on_close)
        
        self.log("高级文件清理工具启动")
    
    def setup_logging(self):
        """设置日志记录"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('advanced_file_cleaner.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def load_default_whitelist(self):
        """加载默认白名单目录"""
        return [
            "Windows", "Program Files", "Program Files (x86)",
            "System32", "SysWOW64", "AppData", "ProgramData",
            "Users", "Documents and Settings"
        ]
    
    def log(self, message, level=logging.INFO):
        """记录日志并更新界面"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        
        if level == logging.INFO:
            self.logger.info(message)
            self.log_text.AppendText(log_message + "\n")
        elif level == logging.WARNING:
            self.logger.warning(message)
            self.log_text.AppendText(f"⚠️ {log_message}\\n")
        elif level == logging.ERROR:
            self.logger.error(message)
            self.log_text.AppendText(f"❌ {log_message}\\n")
        elif level == logging.CRITICAL:
            self.logger.critical(message)
            self.log_text.AppendText(f"💥 {log_message}\\n")
        
        # 滚动到最新日志
        self.log_text.ShowPosition(self.log_text.GetLastPosition())
    
    def create_ui(self):
        """创建用户界面"""
        # 创建笔记本控件（选项卡）
        self.notebook = wx.Notebook(self)
        
        # 创建两个选项卡
        self.tab_ext = wx.Panel(self.notebook)
        self.tab_noext = wx.Panel(self.notebook)
        
        self.notebook.AddPage(self.tab_ext, "按后缀删除")
        self.notebook.AddPage(self.tab_noext, "无后缀文件清理")
        
        # 创建按后缀删除界面
        self.create_extension_tab()
        
        # 创建无后缀文件清理界面
        self.create_noextension_tab()
        
        # 创建底部日志区域
        self.create_log_area()
        
        # 设置主布局
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self.notebook, 1, wx.EXPAND | wx.ALL, 5)
        
        # 日志区域
        log_sizer = wx.BoxSizer(wx.VERTICAL)
        log_label = wx.StaticText(self, label="详细操作日志:")
        log_sizer.Add(log_label, 0, wx.ALL, 5)
        log_sizer.Add(self.log_text, 1, wx.EXPAND | wx.ALL, 5)
        
        main_sizer.Add(log_sizer, 1, wx.EXPAND | wx.ALL, 5)
        
        self.SetSizer(main_sizer)
    
    def create_extension_tab(self):
        """创建按后缀删除选项卡"""
        panel = self.tab_ext
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # 文件夹选择区域
        folder_sizer = wx.BoxSizer(wx.HORIZONTAL)
        folder_label = wx.StaticText(panel, label="选择文件夹:")
        folder_sizer.Add(folder_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        
        self.folder_path_ext = wx.TextCtrl(panel, style=wx.TE_READONLY, size=(400, -1))
        folder_sizer.Add(self.folder_path_ext, 1, wx.EXPAND | wx.RIGHT, 5)
        
        self.browse_btn_ext = wx.Button(panel, label="浏览...")
        folder_sizer.Add(self.browse_btn_ext, 0, wx.ALIGN_CENTER_VERTICAL)
        
        main_sizer.Add(folder_sizer, 0, wx.EXPAND | wx.ALL, 10)
        
        # 文件后缀区域
        ext_sizer = wx.BoxSizer(wx.HORIZONTAL)
        ext_label = wx.StaticText(panel, label="文件后缀:")
        ext_sizer.Add(ext_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        
        self.ext_input_ext = wx.TextCtrl(panel, value=".txt,.log,.tmp", size=(200, -1))
        ext_sizer.Add(self.ext_input_ext, 0, wx.EXPAND | wx.RIGHT, 5)
        
        ext_help = wx.StaticText(panel, label="(多个后缀用逗号分隔，如: .txt,.log)")
        ext_sizer.Add(ext_help, 0, wx.ALIGN_CENTER_VERTICAL)
        
        main_sizer.Add(ext_sizer, 0, wx.EXPAND | wx.ALL, 10)
        
        # 按钮区域
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.scan_btn_ext = wx.Button(panel, label="扫描文件")
        btn_sizer.Add(self.scan_btn_ext, 0, wx.RIGHT, 10)
        
        self.delete_btn_ext = wx.Button(panel, label="执行删除")
        self.delete_btn_ext.Disable()
        btn_sizer.Add(self.delete_btn_ext, 0, wx.RIGHT, 10)
        
        # 删除选项
        self.recycle_option_ext = wx.CheckBox(panel, label="移动到回收站（可恢复）")
        btn_sizer.Add(self.recycle_option_ext, 0, wx.ALIGN_CENTER_VERTICAL)
        
        main_sizer.Add(btn_sizer, 0, wx.ALL, 10)
        
        # 文件列表区域
        files_label = wx.StaticText(panel, label="待删除文件列表:")
        main_sizer.Add(files_label, 0, wx.ALL, 5)
        
        self.files_list_ext = wx.ListCtrl(panel, style=wx.LC_REPORT | wx.BORDER_SUNKEN)
        self.files_list_ext.InsertColumn(0, "文件名", width=300)
        self.files_list_ext.InsertColumn(1, "大小", width=100)
        self.files_list_ext.InsertColumn(2, "修改时间", width=150)
        self.files_list_ext.InsertColumn(3, "路径", width=300)
        main_sizer.Add(self.files_list_ext, 1, wx.EXPAND | wx.ALL, 10)
        
        # 统计信息
        self.stats_text_ext = wx.StaticText(panel, label="找到 0 个文件，总大小 0 KB")
        main_sizer.Add(self.stats_text_ext, 0, wx.ALL, 5)
        
        panel.SetSizer(main_sizer)
        
        # 绑定事件
        self.browse_btn_ext.Bind(wx.EVT_BUTTON, self.on_browse_folder_ext)
        self.scan_btn_ext.Bind(wx.EVT_BUTTON, self.on_scan_files_ext)
        self.delete_btn_ext.Bind(wx.EVT_BUTTON, self.on_delete_files_ext)
    
    def create_noextension_tab(self):
        """创建无后缀文件清理选项卡"""
        panel = self.tab_noext
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # 文件夹选择区域
        folder_sizer = wx.BoxSizer(wx.HORIZONTAL)
        folder_label = wx.StaticText(panel, label="选择扫描目录:")
        folder_sizer.Add(folder_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        
        self.folder_path_noext = wx.TextCtrl(panel, style=wx.TE_READONLY, size=(400, -1))
        folder_sizer.Add(self.folder_path_noext, 1, wx.EXPAND | wx.RIGHT, 5)
        
        self.browse_btn_noext = wx.Button(panel, label="浏览...")
        folder_sizer.Add(self.browse_btn_noext, 0, wx.ALIGN_CENTER_VERTICAL)
        
        main_sizer.Add(folder_sizer, 0, wx.EXPAND | wx.ALL, 10)
        
        # 白名单配置区域
        whitelist_sizer = wx.BoxSizer(wx.VERTICAL)
        whitelist_label = wx.StaticText(panel, label="白名单配置（自动排除重要系统目录）:")
        whitelist_sizer.Add(whitelist_label, 0, wx.ALL, 5)
        
        # 白名单目录显示
        self.whitelist_text = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_READONLY, size=(-1, 80))
        self.whitelist_text.SetValue("\\n".join(self.whitelist_dirs))
        whitelist_sizer.Add(self.whitelist_text, 0, wx.EXPAND | wx.ALL, 5)
        
        # 自定义白名单
        custom_whitelist_sizer = wx.BoxSizer(wx.HORIZONTAL)
        custom_label = wx.StaticText(panel, label="添加自定义白名单:")
        custom_whitelist_sizer.Add(custom_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        
        self.custom_whitelist_input = wx.TextCtrl(panel, size=(200, -1))
        custom_whitelist_sizer.Add(self.custom_whitelist_input, 0, wx.EXPAND | wx.RIGHT, 5)
        
        self.add_whitelist_btn = wx.Button(panel, label="添加")
        custom_whitelist_sizer.Add(self.add_whitelist_btn, 0)
        
        whitelist_sizer.Add(custom_whitelist_sizer, 0, wx.ALL, 5)
        main_sizer.Add(whitelist_sizer, 0, wx.EXPAND | wx.ALL, 10)
        
        # 扫描选项
        options_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.recursive_scan = wx.CheckBox(panel, label="递归扫描子目录")
        self.recursive_scan.SetValue(True)
        options_sizer.Add(self.recursive_scan, 0, wx.RIGHT, 10)
        
        self.include_hidden = wx.CheckBox(panel, label="包含隐藏文件")
        options_sizer.Add(self.include_hidden, 0)
        
        main_sizer.Add(options_sizer, 0, wx.ALL, 10)
        
        # 按钮区域
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.scan_btn_noext = wx.Button(panel, label="扫描无后缀文件")
        btn_sizer.Add(self.scan_btn_noext, 0, wx.RIGHT, 10)
        
        self.delete_btn_noext = wx.Button(panel, label="清理文件")
        self.delete_btn_noext.Disable()
        btn_sizer.Add(self.delete_btn_noext, 0, wx.RIGHT, 10)
        
        # 删除选项
        self.recycle_option_noext = wx.CheckBox(panel, label="移动到回收站（可恢复）")
        self.recycle_option_noext.SetValue(True)  # 默认启用安全删除
        btn_sizer.Add(self.recycle_option_noext, 0, wx.ALIGN_CENTER_VERTICAL)
        
        main_sizer.Add(btn_sizer, 0, wx.ALL, 10)
        
        # 文件列表区域
        files_label = wx.StaticText(panel, label="无后缀文件列表:")
        main_sizer.Add(files_label, 0, wx.ALL, 5)
        
        self.files_list_noext = wx.ListCtrl(panel, style=wx.LC_REPORT | wx.BORDER_SUNKEN)
        self.files_list_noext.InsertColumn(0, "文件名", width=200)
        self.files_list_noext.InsertColumn(1, "大小", width=80)
        self.files_list_noext.InsertColumn(2, "修改时间", width=120)
        self.files_list_noext.InsertColumn(3, "完整路径", width=400)
        main_sizer.Add(self.files_list_noext, 1, wx.EXPAND | wx.ALL, 10)
        
        # 统计信息
        self.stats_text_noext = wx.StaticText(panel, label="找到 0 个无后缀文件，总大小 0 KB")
        main_sizer.Add(self.stats_text_noext, 0, wx.ALL, 5)
        
        panel.SetSizer(main_sizer)
        
        # 绑定事件
        self.browse_btn_noext.Bind(wx.EVT_BUTTON, self.on_browse_folder_noext)
        self.scan_btn_noext.Bind(wx.EVT_BUTTON, self.on_scan_noext_files)
        self.delete_btn_noext.Bind(wx.EVT_BUTTON, self.on_delete_noext_files)
        self.add_whitelist_btn.Bind(wx.EVT_BUTTON, self.on_add_whitelist)
    
    def create_log_area(self):
        """创建日志区域"""
        self.log_text = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2)
    
    def on_browse_folder_ext(self, event):
        """浏览文件夹（按后缀删除）"""
        with wx.DirDialog(self, "选择文件夹", style=wx.DD_DEFAULT_STYLE) as dialog:
            if dialog.ShowModal() == wx.ID_OK:
                self.selected_folder = dialog.GetPath()
                self.folder_path_ext.SetValue(self.selected_folder)
                self.log(f"[按后缀] 选择文件夹: {self.selected_folder}")
                
                # 清空文件列表
                self.files_list_ext.DeleteAllItems()
                self.files_to_delete = []
                self.delete_btn_ext.Disable()
                self.update_stats_ext()
    
    def on_browse_folder_noext(self, event):
        """浏览文件夹（无后缀文件清理）"""
        with wx.DirDialog(self, "选择扫描目录", style=wx.DD_DEFAULT_STYLE) as dialog:
            if dialog.ShowModal() == wx.ID_OK:
                selected_path = dialog.GetPath()
                self.folder_path_noext.SetValue(selected_path)
                self.log(f"[无后缀] 选择扫描目录: {selected_path}")
    
    def on_scan_files_ext(self, event):
        """扫描文件（按后缀删除）"""
        if not self.selected_folder:
            wx.MessageBox("请先选择文件夹！", "提示", wx.OK | wx.ICON_WARNING)
            return
        
        extensions = self.ext_input_ext.GetValue().strip()
        if not extensions:
            wx.MessageBox("请输入文件后缀！", "提示", wx.OK | wx.ICON_WARNING)
            return
        
        # 解析后缀
        ext_list = [ext.strip() for ext in extensions.split(',') if ext.strip()]
        
        self.log(f"[按后缀] 开始扫描文件夹: {self.selected_folder}")
        self.log(f"[按后缀] 目标后缀: {', '.join(ext_list)}")
        
        # 清空文件列表
        self.files_list_ext.DeleteAllItems()
        self.files_to_delete = []
        
        try:
            # 扫描文件
            total_size = 0
            for ext in ext_list:
                pattern = os.path.join(self.selected_folder, f"*{ext}")
                files = glob.glob(pattern, recursive=True)
                
                for file_path in files:
                    if os.path.isfile(file_path):
                        file_info = self.get_file_info(file_path)
                        self.files_to_delete.append(file_info)
                        total_size += file_info['size']
            
            # 更新文件列表
            self.update_files_list_ext()
            self.update_stats_ext()
            
            if self.files_to_delete:
                self.delete_btn_ext.Enable()
                self.log(f"[按后缀] 扫描完成，找到 {len(self.files_to_delete)} 个文件")
            else:
                self.delete_btn_ext.Disable()
                self.log("[按后缀] 未找到匹配的文件")
                
        except Exception as e:
            self.log(f"[按后缀] 扫描文件时出错: {str(e)}", logging.ERROR)
            wx.MessageBox(f"扫描文件时出错: {str(e)}", "错误", wx.OK | wx.ICON_ERROR)
    
    def on_scan_noext_files(self, event):
        """扫描无后缀文件"""
        selected_folder = self.folder_path_noext.GetValue().strip()
        if not selected_folder:
            wx.MessageBox("请先选择扫描目录！", "提示", wx.OK | wx.ICON_WARNING)
            return
        
        if not os.path.exists(selected_folder):
            wx.MessageBox("选择的目录不存在！", "错误", wx.OK | wx.ICON_ERROR)
            return
        
        self.log(f"[无后缀] 开始扫描无后缀文件: {selected_folder}")
        
        # 清空文件列表
        self.files_list_noext.DeleteAllItems()
        self.files_to_delete_noext = []
        
        try:
            # 扫描无后缀文件
            files_found = self.scan_no_extension_files(selected_folder)
            
            # 更新文件列表
            self.update_files_list_noext()
            self.update_stats_noext()
            
            if files_found:
                self.delete_btn_noext.Enable()
                self.log(f"[无后缀] 扫描完成，找到 {len(files_found)} 个无后缀文件")
            else:
                self.delete_btn_noext.Disable()
                self.log("[无后缀] 未找到无后缀文件")
                
        except Exception as e:
            self.log(f"[无后缀] 扫描文件时出错: {str(e)}", logging.ERROR)
            wx.MessageBox(f"扫描文件时出错: {str(e)}", "错误", wx.OK | wx.ICON_ERROR)
    
    def scan_no_extension_files(self, directory):
        """扫描指定目录中的无后缀文件"""
        noext_files = []
        
        try:
            for root, dirs, files in os.walk(directory):
                # 检查是否在白名单中
                if self.is_whitelisted(root):
                    self.log(f"[无后缀] 跳过白名单目录: {root}", logging.INFO)
                    continue
                
                for file in files:
                    file_path = os.path.join(root, file)
                    
                    # 检查是否为无后缀文件
                    if self.is_no_extension_file(file):
                        # 检查文件属性
                        if not self.include_hidden.GetValue() and self.is_hidden_file(file_path):
                            continue
                        
                        file_info = self.get_file_info(file_path)
                        noext_files.append(file_info)
            
            self.files_to_delete_noext = noext_files
            return noext_files
            
        except Exception as e:
            self.log(f"[无后缀] 扫描目录时出错: {str(e)}", logging.ERROR)
            raise e
    
    def is_no_extension_file(self, filename):
        """判断是否为无后缀文件"""
        # 排除有后缀的文件和系统文件
        if '.' in filename:
            return False
        
        # 排除常见的系统无后缀文件
        system_files = ['Thumbs', 'desktop', 'DS_Store', 'localized']
        if filename in system_files:
            return False
            
        return True
    
    def is_whitelisted(self, path):
        """检查路径是否在白名单中"""
        path_parts = Path(path).parts
        for part in path_parts:
            if part in self.whitelist_dirs:
                return True
        return False
    
    def is_hidden_file(self, filepath):
        """检查文件是否为隐藏文件"""
        try:
            return bool(os.stat(filepath).st_file_attributes & 2)  # FILE_ATTRIBUTE_HIDDEN
        except:
            return False
    
    def get_file_info(self, file_path):
        """获取文件信息"""
        stat = os.stat(file_path)
        return {
            'path': file_path,
            'name': os.path.basename(file_path),
            'size': stat.st_size,
            'modified': datetime.datetime.fromtimestamp(stat.st_mtime)
        }
    
    def update_files_list_ext(self):
        """更新按后缀删除的文件列表显示"""
        self.files_list_ext.DeleteAllItems()
        
        for i, file_info in enumerate(self.files_to_delete):
            index = self.files_list_ext.InsertItem(i, file_info['name'])
            
            # 格式化文件大小
            size_kb = file_info['size'] / 1024
            if size_kb < 1024:
                size_str = f"{size_kb:.1f} KB"
            else:
                size_str = f"{size_kb/1024:.1f} MB"
            
            self.files_list_ext.SetItem(index, 1, size_str)
            self.files_list_ext.SetItem(index, 2, file_info['modified'].strftime("%Y-%m-%d %H:%M:%S"))
            self.files_list_ext.SetItem(index, 3, file_info['path'])
    
    def update_files_list_noext(self):
        """更新无后缀文件列表显示"""
        self.files_list_noext.DeleteAllItems()
        
        for i, file_info in enumerate(self.files_to_delete_noext):
            index = self.files_list_noext.InsertItem(i, file_info['name'])
            
            # 格式化文件大小
            size_kb = file_info['size'] / 1024
            if size_kb < 1024:
                size_str = f"{size_kb:.1f} KB"
            else:
                size_str = f"{size_kb/1024:.1f} MB"
            
            self.files_list_noext.SetItem(index, 1, size_str)
            self.files_list_noext.SetItem(index, 2, file_info['modified'].strftime("%Y-%m-%d %H:%M:%S"))
            self.files_list_noext.SetItem(index, 3, file_info['path'])
    
    def update_stats_ext(self):
        """更新按后缀删除的统计信息"""
        total_size = sum(f['size'] for f in self.files_to_delete)
        size_kb = total_size / 1024
        
        if size_kb < 1024:
            size_str = f"{size_kb:.1f} KB"
        else:
            size_str = f"{size_kb/1024:.1f} MB"
        
        self.stats_text_ext.SetLabel(f"找到 {len(self.files_to_delete)} 个文件，总大小 {size_str}")
    
    def update_stats_noext(self):
        """更新无后缀文件统计信息"""
        total_size = sum(f['size'] for f in self.files_to_delete_noext)
        size_kb = total_size / 1024
        
        if size_kb < 1024:
            size_str = f"{size_kb:.1f} KB"
        else:
            size_str = f"{size_kb/1024:.1f} MB"
        
        self.stats_text_noext.SetLabel(f"找到 {len(self.files_to_delete_noext)} 个无后缀文件，总大小 {size_str}")
    
    def on_delete_files_ext(self, event):
        """执行删除操作（按后缀删除）"""
        if not self.files_to_delete:
            wx.MessageBox("没有文件可删除！", "提示", wx.OK | wx.ICON_INFORMATION)
            return
        
        use_recycle = self.recycle_option_ext.GetValue()
        self.perform_deletion(self.files_to_delete, "按后缀", use_recycle)
    
    def on_delete_noext_files(self, event):
        """执行无后缀文件清理"""
        if not hasattr(self, 'files_to_delete_noext') or not self.files_to_delete_noext:
            wx.MessageBox("没有无后缀文件可清理！", "提示", wx.OK | wx.ICON_INFORMATION)
            return
        
        use_recycle = self.recycle_option_noext.GetValue()
        self.perform_deletion(self.files_to_delete_noext, "无后缀", use_recycle)
    
    def perform_deletion(self, files_to_delete, operation_type, use_recycle=True):
        """执行实际的删除操作"""
        # 显示确认对话框
        total_size = sum(f['size'] for f in files_to_delete)
        size_kb = total_size / 1024
        size_str = f"{size_kb:.1f} KB" if size_kb < 1024 else f"{size_kb/1024:.1f} MB"
        
        delete_type = "移动到回收站" if use_recycle else "永久删除"
        
        file_list = "\n".join([f"• {f['name']}" for f in files_to_delete[:10]])  # 只显示前10个
        if len(files_to_delete) > 10:
            file_list += f"\n• ... 还有 {len(files_to_delete) - 10} 个文件"
        
        message = f"确定要{delete_type}以下 {len(files_to_delete)} 个文件吗？\n\n"
        message += f"操作类型: {operation_type}清理\n"
        message += f"删除方式: {delete_type}\n"
        message += f"总大小: {size_str}\n\n"
        message += file_list
        
        dlg = wx.MessageDialog(self, message, "确认删除", 
                              wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING)
        
        if dlg.ShowModal() == wx.ID_YES:
            self.execute_deletion(files_to_delete, operation_type, use_recycle)
        
        dlg.Destroy()
    
    def execute_deletion(self, files_to_delete, operation_type, use_recycle):
        """执行删除操作"""
        self.log(f"[{operation_type}] 开始删除操作...")
        
        success_count = 0
        error_count = 0
        
        for file_info in files_to_delete:
            try:
                if use_recycle:
                    # 使用send2trash移动到回收站
                    send2trash.send2trash(file_info['path'])
                    operation_desc = "移动到回收站"
                else:
                    # 直接删除
                    os.remove(file_info['path'])
                    operation_desc = "永久删除"
                
                self.log(f"✓ [{operation_type}] {operation_desc}成功: {file_info['name']}")
                success_count += 1
                
            except PermissionError:
                self.log(f"❌ [{operation_type}] 权限不足，无法删除: {file_info['name']}", logging.ERROR)
                error_count += 1
                
            except FileNotFoundError:
                self.log(f"❌ [{operation_type}] 文件不存在: {file_info['name']}", logging.WARNING)
                error_count += 1
                
            except Exception as e:
                self.log(f"❌ [{operation_type}] 删除失败 {file_info['name']}: {str(e)}", logging.ERROR)
                error_count += 1
        
        # 显示结果
        delete_type = "移动到回收站" if use_recycle else "永久删除"
        message = f"{operation_type}清理操作完成！\\n\\n"
        message += f"操作方式: {delete_type}\\n"
        message += f"成功处理: {success_count} 个文件\\n"
        message += f"处理失败: {error_count} 个文件"
        
        wx.MessageBox(message, "清理完成", wx.OK | 
                     (wx.ICON_INFORMATION if error_count == 0 else wx.ICON_WARNING))
        
        # 清空文件列表
        if operation_type == "按后缀":
            self.files_list_ext.DeleteAllItems()
            self.files_to_delete = []
            self.delete_btn_ext.Disable()
            self.update_stats_ext()
        else:
            self.files_list_noext.DeleteAllItems()
            self.files_to_delete_noext = []
            self.delete_btn_noext.Disable()
            self.update_stats_noext()
        
        self.log(f"[{operation_type}] 删除操作完成 - 成功: {success_count}, 失败: {error_count}")
    
    def on_add_whitelist(self, event):
        """添加自定义白名单"""
        custom_item = self.custom_whitelist_input.GetValue().strip()
        if custom_item:
            if custom_item not in self.whitelist_dirs:
                self.whitelist_dirs.append(custom_item)
                self.whitelist_text.SetValue("\\n".join(self.whitelist_dirs))
                self.log(f"[白名单] 添加自定义白名单: {custom_item}")
                self.custom_whitelist_input.SetValue("")
            else:
                wx.MessageBox("该白名单项已存在！", "提示", wx.OK | wx.ICON_INFORMATION)
        else:
            wx.MessageBox("请输入白名单项！", "提示", wx.OK | wx.ICON_WARNING)
    
    def on_close(self, event):
        """关闭应用程序"""
        self.log("高级文件清理工具关闭")
        self.Destroy()

def main():
    """主函数"""
    app = wx.App()
    frame = AdvancedFileCleanerApp()
    frame.Show()
    app.MainLoop()

if __name__ == "__main__":
    main()