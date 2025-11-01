#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件删除工具 - wxPython GUI应用程序
功能：选择文件夹路径，指定文件后缀名，安全删除文件
"""

import wx
import wx.adv
import os
import glob
import logging
import datetime
from pathlib import Path

class FileDeleterApp(wx.Frame):
    """主应用程序窗口"""
    
    def __init__(self):
        super().__init__(None, title="文件删除工具", size=(800, 600))
        
        # 设置日志记录
        self.setup_logging()
        
        # 初始化变量
        self.selected_folder = ""
        self.files_to_delete = []
        
        # 创建界面
        self.create_ui()
        
        # 居中显示窗口
        self.Centre()
        
        # 绑定事件
        self.Bind(wx.EVT_CLOSE, self.on_close)
        
        self.log("应用程序启动")
    
    def setup_logging(self):
        """设置日志记录"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('file_deleter.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
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
        panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # 标题
        title = wx.StaticText(panel, label="文件删除工具")
        title_font = wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        title.SetFont(title_font)
        main_sizer.Add(title, 0, wx.ALL | wx.ALIGN_CENTER, 10)
        
        # 分隔线
        main_sizer.Add(wx.StaticLine(panel), 0, wx.EXPAND | wx.ALL, 5)
        
        # 文件夹选择区域
        folder_sizer = wx.BoxSizer(wx.HORIZONTAL)
        folder_label = wx.StaticText(panel, label="选择文件夹:")
        folder_sizer.Add(folder_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        
        self.folder_path = wx.TextCtrl(panel, style=wx.TE_READONLY, size=(400, -1))
        folder_sizer.Add(self.folder_path, 1, wx.EXPAND | wx.RIGHT, 5)
        
        self.browse_btn = wx.Button(panel, label="浏览...")
        folder_sizer.Add(self.browse_btn, 0, wx.ALIGN_CENTER_VERTICAL)
        
        main_sizer.Add(folder_sizer, 0, wx.EXPAND | wx.ALL, 10)
        
        # 文件后缀区域
        ext_sizer = wx.BoxSizer(wx.HORIZONTAL)
        ext_label = wx.StaticText(panel, label="文件后缀:")
        ext_sizer.Add(ext_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        
        self.ext_input = wx.TextCtrl(panel, value=".txt,.log,.tmp", size=(200, -1))
        ext_sizer.Add(self.ext_input, 0, wx.EXPAND | wx.RIGHT, 5)
        
        ext_help = wx.StaticText(panel, label="(多个后缀用逗号分隔，如: .txt,.log)")
        ext_sizer.Add(ext_help, 0, wx.ALIGN_CENTER_VERTICAL)
        
        main_sizer.Add(ext_sizer, 0, wx.EXPAND | wx.ALL, 10)
        
        # 按钮区域
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.scan_btn = wx.Button(panel, label="扫描文件")
        btn_sizer.Add(self.scan_btn, 0, wx.RIGHT, 10)
        
        self.delete_btn = wx.Button(panel, label="执行删除")
        self.delete_btn.Disable()
        btn_sizer.Add(self.delete_btn, 0, wx.RIGHT, 10)
        
        self.clear_btn = wx.Button(panel, label="清空日志")
        btn_sizer.Add(self.clear_btn, 0)
        
        main_sizer.Add(btn_sizer, 0, wx.ALL, 10)
        
        # 文件列表区域
        files_label = wx.StaticText(panel, label="待删除文件列表:")
        main_sizer.Add(files_label, 0, wx.ALL, 5)
        
        self.files_list = wx.ListCtrl(panel, style=wx.LC_REPORT | wx.BORDER_SUNKEN)
        self.files_list.InsertColumn(0, "文件名", width=300)
        self.files_list.InsertColumn(1, "大小", width=100)
        self.files_list.InsertColumn(2, "修改时间", width=150)
        main_sizer.Add(self.files_list, 1, wx.EXPAND | wx.ALL, 10)
        
        # 统计信息
        self.stats_text = wx.StaticText(panel, label="找到 0 个文件，总大小 0 KB")
        main_sizer.Add(self.stats_text, 0, wx.ALL, 5)
        
        # 日志区域
        log_label = wx.StaticText(panel, label="操作日志:")
        main_sizer.Add(log_label, 0, wx.ALL, 5)
        
        self.log_text = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2)
        main_sizer.Add(self.log_text, 1, wx.EXPAND | wx.ALL, 10)
        
        # 设置面板布局
        panel.SetSizer(main_sizer)
        
        # 绑定事件
        self.browse_btn.Bind(wx.EVT_BUTTON, self.on_browse_folder)
        self.scan_btn.Bind(wx.EVT_BUTTON, self.on_scan_files)
        self.delete_btn.Bind(wx.EVT_BUTTON, self.on_delete_files)
        self.clear_btn.Bind(wx.EVT_BUTTON, self.on_clear_log)
        self.files_list.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_file_selected)
    
    def on_browse_folder(self, event):
        """浏览文件夹"""
        with wx.DirDialog(self, "选择文件夹", style=wx.DD_DEFAULT_STYLE) as dialog:
            if dialog.ShowModal() == wx.ID_OK:
                self.selected_folder = dialog.GetPath()
                self.folder_path.SetValue(self.selected_folder)
                self.log(f"选择文件夹: {self.selected_folder}")
                
                # 清空文件列表
                self.files_list.DeleteAllItems()
                self.files_to_delete = []
                self.delete_btn.Disable()
                self.update_stats()
    
    def on_scan_files(self, event):
        """扫描文件"""
        if not self.selected_folder:
            wx.MessageBox("请先选择文件夹！", "提示", wx.OK | wx.ICON_WARNING)
            return
        
        extensions = self.ext_input.GetValue().strip()
        if not extensions:
            wx.MessageBox("请输入文件后缀！", "提示", wx.OK | wx.ICON_WARNING)
            return
        
        # 解析后缀
        ext_list = [ext.strip() for ext in extensions.split(',') if ext.strip()]
        
        self.log(f"开始扫描文件夹: {self.selected_folder}")
        self.log(f"目标后缀: {', '.join(ext_list)}")
        
        # 清空文件列表
        self.files_list.DeleteAllItems()
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
            self.update_files_list()
            self.update_stats()
            
            if self.files_to_delete:
                self.delete_btn.Enable()
                self.log(f"扫描完成，找到 {len(self.files_to_delete)} 个文件")
            else:
                self.delete_btn.Disable()
                self.log("未找到匹配的文件")
                
        except Exception as e:
            self.log(f"扫描文件时出错: {str(e)}", logging.ERROR)
            wx.MessageBox(f"扫描文件时出错: {str(e)}", "错误", wx.OK | wx.ICON_ERROR)
    
    def get_file_info(self, file_path):
        """获取文件信息"""
        stat = os.stat(file_path)
        return {
            'path': file_path,
            'name': os.path.basename(file_path),
            'size': stat.st_size,
            'modified': datetime.datetime.fromtimestamp(stat.st_mtime)
        }
    
    def update_files_list(self):
        """更新文件列表显示"""
        self.files_list.DeleteAllItems()
        
        for i, file_info in enumerate(self.files_to_delete):
            index = self.files_list.InsertItem(i, file_info['name'])
            
            # 格式化文件大小
            size_kb = file_info['size'] / 1024
            if size_kb < 1024:
                size_str = f"{size_kb:.1f} KB"
            else:
                size_str = f"{size_kb/1024:.1f} MB"
            
            self.files_list.SetItem(index, 1, size_str)
            self.files_list.SetItem(index, 2, file_info['modified'].strftime("%Y-%m-%d %H:%M:%S"))
    
    def update_stats(self):
        """更新统计信息"""
        total_size = sum(f['size'] for f in self.files_to_delete)
        size_kb = total_size / 1024
        
        if size_kb < 1024:
            size_str = f"{size_kb:.1f} KB"
        else:
            size_str = f"{size_kb/1024:.1f} MB"
        
        self.stats_text.SetLabel(f"找到 {len(self.files_to_delete)} 个文件，总大小 {size_str}")
    
    def on_delete_files(self, event):
        """执行删除操作"""
        if not self.files_to_delete:
            wx.MessageBox("没有文件可删除！", "提示", wx.OK | wx.ICON_INFORMATION)
            return
        
        # 显示确认对话框
        total_size = sum(f['size'] for f in self.files_to_delete)
        size_kb = total_size / 1024
        size_str = f"{size_kb:.1f} KB" if size_kb < 1024 else f"{size_kb/1024:.1f} MB"
        
        file_list = "\n".join([f"• {f['name']}" for f in self.files_to_delete[:10]])  # 只显示前10个
        if len(self.files_to_delete) > 10:
            file_list += f"\n• ... 还有 {len(self.files_to_delete) - 10} 个文件"
        
        message = f"确定要删除以下 {len(self.files_to_delete)} 个文件吗？\n\n"
        message += f"总大小: {size_str}\n\n"
        message += file_list
        
        dlg = wx.MessageDialog(self, message, "确认删除", 
                              wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING)
        
        if dlg.ShowModal() == wx.ID_YES:
            self.perform_deletion()
        
        dlg.Destroy()
    
    def perform_deletion(self):
        """执行实际的删除操作"""
        self.log("开始删除文件...")
        
        success_count = 0
        error_count = 0
        
        for file_info in self.files_to_delete:
            try:
                os.remove(file_info['path'])
                self.log(f"✓ 删除成功: {file_info['name']}")
                success_count += 1
                
            except PermissionError:
                self.log(f"❌ 权限不足，无法删除: {file_info['name']}", logging.ERROR)
                error_count += 1
                
            except FileNotFoundError:
                self.log(f"❌ 文件不存在: {file_info['name']}", logging.WARNING)
                error_count += 1
                
            except Exception as e:
                self.log(f"❌ 删除失败 {file_info['name']}: {str(e)}", logging.ERROR)
                error_count += 1
        
        # 显示结果
        message = f"删除操作完成！\\n\\n"
        message += f"成功删除: {success_count} 个文件\\n"
        message += f"删除失败: {error_count} 个文件"
        
        wx.MessageBox(message, "删除完成", wx.OK | 
                     (wx.ICON_INFORMATION if error_count == 0 else wx.ICON_WARNING))
        
        # 清空文件列表
        self.files_list.DeleteAllItems()
        self.files_to_delete = []
        self.delete_btn.Disable()
        self.update_stats()
        
        self.log(f"删除操作完成 - 成功: {success_count}, 失败: {error_count}")
    
    def on_file_selected(self, event):
        """文件列表项被选中"""
        index = event.GetIndex()
        if 0 <= index < len(self.files_to_delete):
            file_info = self.files_to_delete[index]
            self.log(f"选中文件: {file_info['name']} ({file_info['size']} 字节)")
    
    def on_clear_log(self, event):
        """清空日志"""
        self.log_text.Clear()
        self.log("日志已清空")
    
    def on_close(self, event):
        """关闭应用程序"""
        self.log("应用程序关闭")
        self.Destroy()

def main():
    """主函数"""
    app = wx.App()
    frame = FileDeleterApp()
    frame.Show()
    app.MainLoop()

if __name__ == "__main__":
    main()