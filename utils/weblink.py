import re
import subprocess

def get_ethernet_ip(adapter_name):
    """
    获取指定以太网适配器的IPv4地址
    :param adapter_name: 以太网适配器名称（如"以太网"或"Ethernet"）
    :return: 匹配的IPv4地址字符串，未找到返回None
    """
    # 执行ipconfig命令获取网络配置信息
    result = subprocess.run(['ipconfig', '/all'], capture_output=True, text=True, encoding='gbk')
    output = result.stdout

    # 编译正则表达式
    adapter_pattern = re.compile(rf"^.*{adapter_name}.*:$", re.MULTILINE)
    ip_pattern = re.compile(r"IPv4 地址[\. ]+: ([\d\.]+)")

    # 查找所有适配器块的位置
    adapter_blocks = []
    for match in adapter_pattern.finditer(output):
        start_pos = match.end()
        next_block = adapter_pattern.search(output[start_pos:])
        end_pos = start_pos + next_block.start() if next_block else len(output)
        adapter_blocks.append((start_pos, end_pos))

    # 在匹配的适配器块中搜索IP地址
    for start, end in adapter_blocks:
        block = output[start:end]
        ip_match = ip_pattern.search(block)
        if ip_match:
            print("ipv4:",ip_match.group(1))
            return ip_match.group(1)

    return None

# 示例用法
if __name__ == "__main__":
    adapter = "以太网"  # 修改为你的适配器名称
    ip_address = get_ethernet_ip(adapter)
    if ip_address:
        print(f"适配器 '{adapter}' 的IPv4地址: {ip_address}")
    else:
        print(f"未找到适配器 '{adapter}' 的IPv4地址")