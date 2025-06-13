import logging

class Logger:
    def __init__(self, name, log_file="app.log"): # Thêm tham số log_file để chỉ định tên file log
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        # Xóa các handler hiện có để tránh log bị lặp lại nếu bạn khởi tạo lại Logger
        if not self.logger.handlers:
            # Ghi log ra console
            stream_handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            stream_handler.setFormatter(formatter)
            self.logger.addHandler(stream_handler)

            # Ghi log ra file
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
    
    def info(self, message):
        self.logger.info("✅ "+message)
    
    def error(self, message):
        self.logger.error("❌ "+message)
    
    def debug(self, message):
        self.logger.debug("🔥 "+message)
    
    def warning(self, message):
        self.logger.warning("⚠️ "+message)