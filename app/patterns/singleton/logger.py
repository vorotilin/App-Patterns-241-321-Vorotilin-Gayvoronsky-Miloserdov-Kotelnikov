class Logger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.logs = []
        return cls._instance
    
    def log(self, message):
        self.logs.append(message)
        import sys
        try:
            print(f"[LOG] {message}")
        except UnicodeEncodeError:
            sys.stdout.buffer.write(f"[LOG] {message}\n".encode('utf-8'))
            sys.stdout.buffer.flush()
    
    def get_logs(self):
        return self.logs
    
    def clear(self):
        self.logs = []