import argparse
import os

# os.getenv 方法从环境中获取变量值，如果环境中没有设置这些变量，则使用默认值
os.environ['RANK'] = os.getenv('RANK', '0')
os.environ['WORLD_SIZE'] = os.getenv('WORLD_SIZE', '2')
os.environ['MASTER_ADDR'] = os.getenv('MASTER_ADDR', 'localhost')
os.environ['MASTER_PORT'] = os.getenv('MASTER_PORT', '12356')
os.environ['OMP_NUM_THREADS'] = '4'  # 根据你的系统配置调整线程数

# 创建一个ArgumentParser对象
parser = argparse.ArgumentParser(description='VadCLIP, BLIP, and Llama')

# 添加VadCLIP的参数
parser.add_argument('--vadclip-path', default='vadclip/model_ucf.pth')
parser.add_argument('--vadclip-device', default='cuda:2')
parser.add_argument('--seed', default=234, type=int)
parser.add_argument('--classes-num', default=14, type=int)
parser.add_argument('--embed-dim', default=512, type=int)
parser.add_argument('--visual-length', default=256, type=int)
parser.add_argument('--visual-width', default=512, type=int)
parser.add_argument('--visual-head', default=1, type=int)
parser.add_argument('--visual-layers', default=2, type=int)
parser.add_argument('--attn-window', default=8, type=int)
parser.add_argument('--prompt-prefix', default=10, type=int)
parser.add_argument('--prompt-postfix', default=10, type=int)

# 添加CLIP的参数
parser.add_argument('--clip-device', default='cuda:2')

# 添加BLIP的参数
parser.add_argument('--blip-path', default='blip/')
parser.add_argument('--blip-device', default='cuda:3')

# 添加Llama的参数
parser.add_argument('--llama-path', default='llama/llama-2-13b-chat/')
parser.add_argument('--llama-tokenizer', default='llama/tokenizer.model')
parser.add_argument('--max_seq_len', default=512, type=int)
parser.add_argument('--max_batch_size', default=8, type=int)
