import socket
import datetime
import logging
import os
import time
from logging.handlers import TimedRotatingFileHandler

def setup_logger(log_file_prefix='udp_received'):
    """设置日志记录器，每天自动创建新的日志文件"""
    logger = logging.getLogger('UDPListener')
    logger.setLevel(logging.INFO)
    
    # 避免重复添加handler
    if not logger.handlers:
        # 创建按天轮转的file handler
        # 文件名格式: udp_received.log, udp_received.log.2024-01-01, 等等
        log_file = f"{log_file_prefix}.log"
        handler = TimedRotatingFileHandler(
            log_file, 
            when='midnight',  # 每天午夜轮转
            interval=1,       # 间隔1天
            backupCount=0,    # 设置为0表示永久保留所有历史文件
            encoding='utf-8'
        )
        
        # 设置日志文件名格式
        handler.suffix = "%Y-%m-%d"  # 添加日期后缀
        
        # 设置格式：时间戳 - 消息内容
        formatter = logging.Formatter('%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        handler.setFormatter(formatter)
        
        logger.addHandler(handler)
        
        # 添加控制台handler，便于实时查看
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    return logger

def get_current_log_filename(prefix='udp_received'):
    """获取当前正在写入的日志文件名"""
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    return f"{prefix}.log.{today}"

def main():
    # 监听端口
    UDP_PORT = 9999
    # 日志文件前缀
    LOG_PREFIX = 'udp_received'
    
    # 创建UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    try:
        # 绑定到所有接口的9999端口
        sock.bind(('0.0.0.0', UDP_PORT))
        print(f"开始监听UDP端口 {UDP_PORT}...")
        print(f"日志文件将按天自动保存:")
        print(f"  - 当前文件: {get_current_log_filename(LOG_PREFIX)}")
        print(f"  - 历史文件: {LOG_PREFIX}.log.YYYY-MM-DD")
        print("所有日志文件永久保留，永不删除")
        print("按 Ctrl+C 停止程序")
        
        # 设置日志
        logger = setup_logger(LOG_PREFIX)
        
        # 记录启动信息
        logger.info("=" * 50)
        logger.info("UDP监听服务启动")
        logger.info(f"监听端口: {UDP_PORT}")
        logger.info("=" * 50)
        
        last_date_check = datetime.datetime.now().date()
        
        while True:
            # 接收数据，缓冲区大小为65535字节（UDP最大包大小）
            data, addr = sock.recvfrom(65535)
            
            # 检查日期是否变化，如果变化则提示当前文件名
            current_date = datetime.datetime.now().date()
            if current_date != last_date_check:
                last_date_check = current_date
                logger.info(f"新的一天开始，日志将写入: {get_current_log_filename(LOG_PREFIX)}")
            
            # 解码数据（假设为UTF-8文本）
            try:
                message = data.decode('utf-8').strip()
            except UnicodeDecodeError:
                # 如果不是UTF-8，尝试忽略错误进行解码
                message = data.decode('utf-8', errors='ignore').strip()
                logger.warning(f"收到非UTF-8编码数据，已忽略错误字符")
            
            # 记录到文件（包含时间戳和来源）
            logger.info(f"来自 {addr[0]}:{addr[1]} - {message}")
            
    except KeyboardInterrupt:
        print("\n" + "=" * 50)
        print("程序已停止")
        print(f"日志文件位置: {os.path.abspath('.')}")
        print("文件列表:")
        for file in sorted(os.listdir('.')):
            if file.startswith(LOG_PREFIX) and file.endswith(('.log', '.log.')):
                print(f"  - {file}")
        print("=" * 50)
    except Exception as e:
        print(f"发生错误: {e}")
    finally:
        sock.close()

if __name__ == "__main__":
    main()
