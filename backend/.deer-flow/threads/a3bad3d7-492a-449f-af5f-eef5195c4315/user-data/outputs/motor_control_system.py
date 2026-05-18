import random
import time
from threading import Thread
from transitions import Machine

class MotorController:
    """
    电机控制系统类，包含状态机、电机模型和过载保护功能
    """
    # 定义状态机状态
    states = ['idle', 'running', 'overload']

    def __init__(self):
        # 初始化状态机
        self.machine = Machine(
            model=self,
            states=MotorController.states,
            initial='idle',
            ignore_invalid_triggers=True
        )

        # 添加状态转换
        self.machine.add_transition(
            trigger='start', 
            source='idle', 
            dest='running',
            before='_before_start',
            after='_after_start'
        )
        self.machine.add_transition(
            trigger='stop', 
            source='running', 
            dest='idle',
            after='_after_stop'
        )
        self.machine.add_transition(
            trigger='trigger_overload', 
            source='running', 
            dest='overload',
            after='_after_overload'
        )
        self.machine.add_transition(
            trigger='reset_overload', 
            source='overload', 
            dest='idle',
            after='_after_reset'
        )

        # 电机参数
        self.set_speed = 0.0          # 设定速度(0-100%)
        self.current_speed = 0.0      # 当前速度(0-100%)
        self.current_current = 0.0    # 当前电流(A)
        self.overload_threshold = 10.0 # 过载阈值(A)
        self.overload_count = 0       # 过载检测计数器
        self.running = False          # 运行标志

    # 状态转换钩子函数
    def _before_start(self):
        """启动前的准备工作"""
        self.set_speed = 0.0
        self.current_speed = 0.0

    def _after_start(self):
        """启动后的处理"""
        self.running = True
        print("电机已启动")

    def _after_stop(self):
        """停止后的处理"""
        self.running = False
        print("电机已停止")

    def _after_overload(self):
        """过载后的处理"""
        self.running = False
        self.set_speed = 0.0
        print("⚠️  过载保护触发！电机已停止")

    def _after_reset(self):
        """复位后的处理"""
        self.overload_count = 0
        self.current_current = 0.0
        print("过载保护已复位")

    # 控制方法
    def set_speed_value(self, speed):
        """设置电机速度(0-100%)"""
        if 0 <= speed <= 100:
            self.set_speed = speed
            print(f"设定速度：{speed}%")
        else:
            print("❌ 速度必须在0-100之间")

    def update_state(self):
        """更新电机状态（应该在后台线程中运行）"""
        while True:
            if self.running:
                # 模拟速度响应（一阶惯性系统）
                speed_error = self.set_speed - self.current_speed
                self.current_speed += speed_error * 0.1

                # 模拟电流计算（速度*系数+负载波动）
                base_current = self.current_speed * 0.1
                load_variation = random.uniform(-0.5, 1.5)  # 模拟负载变化
                self.current_current = base_current + load_variation

                # 过载检测（连续5次超过阈值触发保护）
                if self.current_current > self.overload_threshold:
                    self.overload_count += 1
                    if self.overload_count >= 5:
                        self.trigger_overload()
                else:
                    self.overload_count = 0
            else:
                # 停止时速度和电流逐渐归零
                if self.current_speed > 0:
                    self.current_speed -= 2.0
                    self.current_current = self.current_speed * 0.1
                else:
                    self.current_speed = 0.0
                    self.current_current = 0.0

            time.sleep(0.1)  # 100ms更新一次

    def get_status(self):
        """获取当前状态信息"""
        return {
            'state': self.state,
            'set_speed': round(self.set_speed, 1),
            'current_speed': round(self.current_speed, 1),
            'current_current': round(self.current_current, 2),
            'overload_threshold': self.overload_threshold
        }

def main():
    """主函数：用户交互界面"""
    motor = MotorController()

    # 启动状态更新线程
    update_thread = Thread(target=motor.update_state)
    update_thread.daemon = True
    update_thread.start()

    print("=" * 50)
    print("电机控制系统 v1.0")
    print("命令列表：")
    print("  start    - 启动电机")
    print("  stop     - 停止电机")
    print("  speed N  - 设置速度N(0-100)")
    print("  status   - 查看状态")
    print("  reset    - 复位过载保护")
    print("  exit     - 退出系统")
    print("=" * 50)

    while True:
        try:
            command = input("\n> ").strip().lower()
            
            if command == 'start':
                motor.start()
            elif command == 'stop':
                motor.stop()
            elif command.startswith('speed'):
                parts = command.split()
                if len(parts) == 2:
                    try:
                        speed = float(parts[1])
                        motor.set_speed_value(speed)
                    except ValueError:
                        print("❌ 请输入有效的数字")
                else:
                    print("❌ 使用方法：speed <0-100>")
            elif command == 'status':
                status = motor.get_status()
                print(f"\n当前状态：{status['state']}")
                print(f"设定速度：{status['set_speed']}%")
                print(f"当前速度：{status['current_speed']}%")
                print(f"当前电流：{status['current_current']}A")
                print(f"过载阈值：{status['overload_threshold']}A")
            elif command == 'reset':
                motor.reset_overload()
            elif command == 'exit':
                print("系统退出")
                break
            elif command == '':
                continue
            else:
                print(f"❌ 未知命令：{command}")
                
        except KeyboardInterrupt:
            print("\n系统退出")
            break
        except Exception as e:
            print(f"❌ 发生错误：{e}")

if __name__ == "__main__":
    main()