import json

class Bill:
    def __init__(self, bill_id, pile_id, user_id, t, begin_time, end_time, amount, cost_time,
             charge_fee, service_fee, total):
        self.pile_id = pile_id
        self.user_id = user_id
        self.charge_fee = charge_fee
        self.service_fee = service_fee
        self.total = total
        self.t = t
        self.bill_id = bill_id
        self.amount = amount
        self.cost_time = cost_time
        self.begin_time = begin_time
        self.end_time = end_time
        self.jso = {
            '详单编号': self.bill_id,
            '用户编号': self.user_id,
            '详单生成时间': '{:02}:{:02}:{:02}'.
                format(self.t // 3600, self.t % 3600 // 60, self.t % 60),
            '充电桩编号': self.pile_id,
            '充电电量': self.amount,
            '充电时长': f'{self.cost_time}分钟',
            '启动时间': '{:02}:{:02}:{:02}'.
                format(self.begin_time // 3600, self.begin_time % 3600 // 60, self.begin_time % 60),
            '停止时间': '{:02}:{:02}:{:02}'.
                format(self.end_time // 3600, self.end_time % 3600 // 60, self.end_time % 60),
            '充电费用': self.charge_fee,
            '服务费用': self.service_fee,
            '总费用': self.total
        }
        with open('.\\bill\\{}_{}_{}.{}.{}.json'.\
                format(bill_id, user_id, t // 3600, t % 3600 // 60, t % 60), 'w',encoding='utf-8') as f:
            json.dump(self.jso, f, ensure_ascii=False, indent=4)

class User:
    def __init__(self, user_id, queue_number, mode, amount, begin_wait):
        self.user_id = user_id
        # self.pile_id = 0
        self.queue_number = queue_number
        self.mode = mode
        self.amount = amount
        self.begin_wait = begin_wait
        self.begin_time = 0
        self.cost_time = 0
        self.end_time = 0
    
