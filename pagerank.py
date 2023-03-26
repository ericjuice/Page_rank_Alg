import shutil

size = 1000
meaningful_num = 0  # 记录非完全孤立的节点,即公式中的N
max_num = 0  # 存放最大的数，用于划分循环次数
e = 10  # 收敛限
beta = 0.85
m_name = 'sparse_matrix_'


def get_total_size():
    global max_num
    f_data = open('data.txt', 'r', encoding="utf-16")
    for line in f_data:
        row = line.strip()
        my_num = row.split(" ")
        my_num = str_to_num(my_num)
        if max_num < my_num[0]:
            max_num = my_num[0]
        if max_num < my_num[1]:
            max_num = my_num[1]


def str_to_num(str_list):
    str_list = [int(x) for x in str_list]
    return str_list


def write_temp():  # temp文件存放id,入度，出度，出节点。这里遍历了max_num/size+1次data
    data_index = 0  # 用于计数
    f_temp = open("temp.txt", 'w', encoding="utf-16")
    f_temp1 = open("temp1.txt", 'w', encoding="utf-16")
    for i in range(0, (max_num + 1) // size + 1):  # max_num/size+1次写入，一次写入size行
        f_data = open('data.txt', 'r', encoding="utf-16")
        p = []  # p是size长度的列表，存放index、入度，出度、出节点
        for j in range(0, size):  # p初始化,一次size个p
            temp_list = [data_index, 0, 0, []]
            data_index += 1
            p.append(temp_list)
        line = f_data.readline()
        while line:  # 遍历一遍data，写入size个p
            my_num = line.strip().split(' ')
            my_num = str_to_num(my_num)
            line = f_data.readline()
            # 本次要找的是size大小区间的数.如果num[0]在范围内，说明它指向后面的节点.反之亦然
            if my_num[0] in range(data_index - size, data_index):
                p[my_num[0] % size][2] += 1  # 出度++
                p[my_num[0] % size][3].append(my_num[1])  # 出节点
            if my_num[1] in range(data_index - size, data_index):
                p[my_num[1] % size][1] += 1  # 入度++

        global meaningful_num
        for temp_p in p:
            if temp_p[1] == 0 and temp_p[2] == 0:  # 入度出度都是0，即完全孤立的节点，舍去
                continue
            if temp_p[1] == 0 and temp_p[2] != 0:  #
                print(str(temp_p[0]) + " 0", file=f_temp1)
            s = str(temp_p).replace('[', '').replace(']', '').replace(',', '')
            print(s, file=f_temp)
            meaningful_num += 1
        f_data.close()
    f_temp.close()
    f_temp1.close()


def write_mi_r():  # 这里写入m文件和r文件，遍历了max_num/size+1次temp
    f_r_new = open('r_new.txt', 'w', encoding="utf-16")
    f_r_old = open('r_old.txt', 'w', encoding="utf-16")
    for i in range(0, (max_num + 1) // size + 1):  # 写入max_num/size+1个文件
        real_name = m_name + str(i) + ".txt"  # 以mi命名
        f_temp = open('temp.txt', 'r', encoding="utf-16")
        f_mi = open(real_name, 'w', encoding="utf-16")
        for line in f_temp:
            temp_list = str_to_num(line.strip().split(' '))  # temp_list包括id,入度，出度，出列表
            if i == 0:  # 第一次的时候顺便写入r
                print(str(temp_list[0]) + ' 0', file=f_r_old)
                print(str(temp_list[0]) + ' 1', file=f_r_new)
            if temp_list[2] == 0:  # 出度为0，不用记录入m
                continue
            p = [temp_list[0], temp_list[2], []]  # 用p做临时变量，这次p包括id,出度、出节点
            out_list = temp_list[3:]  # 一行的出节点列表
            for nums in out_list:
                if nums in range(i * size, (i + 1) * size):  # 筛选出mi范围内的值
                    p[2].append(nums)
            if len(p[2]) == 0:  # p没有本次范围内的出节点，不用记录
                continue
            s = str(p).replace('[', '').replace(']', '').replace(',', '')
            print(s, file=f_mi)
        f_temp.close()
        f_mi.close()
    f_r_new.close()
    f_r_old.close()


def converged():  # 判断收敛
    f_old = open("r_old.txt", 'r', encoding="utf-16")
    f_new = open("r_new.txt", 'r', encoding="utf-16")
    old_line = f_old.readline()
    new_line = f_new.readline()
    result = 0.0
    while old_line:
        old_list = float(old_line.strip().split(' ')[1])
        new_list = float(new_line.strip().split(' ')[1])
        result += abs(old_list - new_list)
        old_line = f_old.readline()
        new_line = f_new.readline()
    f_old.close()
    f_new.close()
    if result > e:
        return False
    else:
        return True


def refine_leak():
    f_buff = open("r_buff.txt", 'w+', encoding="utf-16")
    s = 0.0
    f_new = open("r_new.txt", 'r', encoding="utf-16")
    new_line = f_new.readline()
    while new_line:  # 先扫一遍，求和
        new_list = new_line.strip().split(' ')
        s += float(new_list[1])
        new_line = f_new.readline()
    f_new.close()
    bias = 0
    if meaningful_num != 0:
        bias = 1.0 - (s / meaningful_num)  # optimize2
    f_new = open("r_new.txt", 'r', encoding="utf-16")
    new_line = f_new.readline()
    while new_line:  # 再扫一遍，写入buff
        new_list = new_line.strip().split(' ')
        key = new_list[0]
        value = float(new_list[1]) + bias
        print(key + ' ' + str(value), file=f_buff)
        new_line = f_new.readline()
    f_new.close()
    f_buff.close()
    # 复制文件
    shutil.copyfile("r_buff.txt", "r_new.txt")


def calculate():
    while not converged():
        # new复制给old
        shutil.copyfile("r_new.txt", "r_old.txt")
        f_new = open("r_new.txt", 'w+', encoding="utf-16")
        for i in range(0, (max_num + 1) // size + 1):  # 每次计算一小块，范围是size*i到size*(i+1)
            f_m = open(m_name + str(i) + ".txt", 'r', encoding="utf-16")
            # 声明2部字典
            r_new = dict()
            for line in f_m:  # m块的每一行的每一个节点，都要加上β*score/degree
                t = str_to_num(line.strip().split(' '))
                m_line = [t[0], t[1], t[2:]]  # 此时m_line 存放id，出度，出节点
                f_old = open("r_old.txt", 'r', encoding="utf-16")  # optimize 1
                old_line = f_old.readline().strip().split(' ')  # 此处寻找r_old里id对应的值
                while int(old_line[0]) != m_line[0]:
                    old_line = f_old.readline().strip().split(' ')
                old_value = old_line[1]
                f_old.close()

                for items in m_line[2]:
                    new_value = r_new.get(items, 0.0)
                    new_value += beta * float(old_value) / float(m_line[1])
                    # 加上β*score/d
                    r_new[items] = new_value
            f_m.close()
            # 此时r_new存放了本块范围内的节点值，现在写入f_new
            keys = list(r_new.keys())
            values = list(r_new.values())
            for k in range(0, len(keys)):
                print(str(keys[k]) + ' ' + str(values[k]), file=f_new)

        f_new.close()
        fp = open('temp1.txt', 'r', encoding="utf-16")
        fq = open('r_new.txt', 'a', encoding="utf-16")  # 这里用追加模式
        for line in fp:
            fq.write(line)
        fp.close()
        fq.close()
        # 完成之后，补上leak
        refine_leak()


def my_sort(mid_list):  # 这里先用升序排列
    for i in range(0, len(mid_list)):
        min_item = mid_list[i]
        min_num = i
        for j in range(i + 1, len(mid_list)):
            if mid_list[j][1] < min_item[1]:
                min_num = j
                min_item = mid_list[j]
        # if min_num != i:
        #     temp = mid_list[i]
        #     mid_list[i] = mid_list[j]
        #     mid_list[j] = temp
    return mid_list


def my_insert(mid_list, insert_list):  # 由于刚刚用的是升序排列，所以从最开始开始比较即可
    if insert_list[1] > mid_list[0][1]:
        mid_list[0] = insert_list
    for i in range(1, len(mid_list)):
        if mid_list[i - 1][1] > mid_list[i][1]:
            temp = mid_list[i - 1]
            mid_list[i - 1] = mid_list[i]
            mid_list[i] = temp
        else:
            break
    return mid_list


def select_top():  # 选取最终的前100个点
    f_new = open("r_new.txt", 'r', encoding="utf-16")
    top_one_hundred = []
    for i in range(0, 100):
        mid_str = f_new.readline().strip().split(' ')
        mid_num = [float(x) for x in mid_str]
        top_one_hundred.append(mid_num)
        top_one_hundred = my_sort(top_one_hundred)
    for line in f_new:
        midStr = line.strip().split(' ')
        mid = [float(x) for x in midStr]
        top_one_hundred = my_insert(top_one_hundred, mid)
    top_one_hundred = top_one_hundred[::-1]  # 翻转列表
    f_new.close()
    f_top = open("top100.txt", 'w+', encoding="utf-16")
    for k in range(0, len(top_one_hundred)):
        print('[' + str(int(top_one_hundred[k][0])) + ']\t[' + str(top_one_hundred[k][1]) + ']', file=f_top)
    f_top.close()


get_total_size()
write_temp()
write_mi_r()
calculate()
select_top()

print("The project have done!")
