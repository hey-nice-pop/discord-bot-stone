import discord
import random

def generate_minesweeper_board(width, height, num_mines):
    # 初期盤面の生成
    board = [['0' for _ in range(width)] for _ in range(height)]

    # 地雷を配置
    for _ in range(num_mines):
        x, y = random.randint(0, width - 1), random.randint(0, height - 1)
        while board[y][x] == '💣':
            x, y = random.randint(0, width - 1), random.randint(0, height - 1)
        board[y][x] = '💣'

    # 隣接する地雷の数を計算
    for y in range(height):
        for x in range(width):
            if board[y][x] == '💣':
                continue
            mines_count = 0
            # 隣接する8セルをチェック
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < width and 0 <= ny < height:
                        if board[ny][nx] == '💣':
                            mines_count += 1
            board[y][x] = str(mines_count)  # 地雷の数をセット

    return board

def format_minesweeper_board(board):
    # 盤面を整形して文字列にする
    emoji_map = {'0': '0️⃣', '1': '1️⃣', '2': '2️⃣', '3': '3️⃣', '4': '4️⃣', '5': '5️⃣', '6': '6️⃣', '7': '7️⃣', '8': '8️⃣', '💣': '💣'}
    formatted_board = '\n'.join([''.join(f'||{emoji_map[cell]}||' for cell in row) for row in board])
    return formatted_board

def play(width, height, num_mines):
    if width < 1 or height < 1 or width > 20 or height > 20:
        return "幅と高さは1から20の間で指定してください。"

    board = generate_minesweeper_board(width, height, num_mines)
    return format_minesweeper_board(board)

def setup(bot):
    @bot.tree.command(name="minesweeper", description="マインスイーパーをプレイ")
    async def minesweeper_command(interaction: discord.Interaction, width: int, height: int, num_mines: int):
        await interaction.response.send_message(play(width, height, num_mines))