import discord
import random
from discord import app_commands

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

def format_minesweeper_board(board, revealed_positions=None):
    # 盤面を整形して文字列にする
    emoji_map = {
        '0': '0️⃣',
        '1': '1️⃣',
        '2': '2️⃣',
        '3': '3️⃣',
        '4': '4️⃣',
        '5': '5️⃣',
        '6': '6️⃣',
        '7': '7️⃣',
        '8': '8️⃣',
        '💣': '💣',
    }
    revealed_positions = revealed_positions or set()
    lines = []
    for y, row in enumerate(board):
        cells = []
        for x, cell in enumerate(row):
            emoji = emoji_map[cell]
            if (x, y) in revealed_positions:
                cells.append(emoji)
            else:
                cells.append(f'||{emoji}||')
        lines.append(''.join(cells))
    return '\n'.join(lines)

def validate_minesweeper_input(width, height, num_mines, reveal_safe):
    if width < 1 or height < 1 or width > 20 or height > 20:
        return "幅と高さは1から20の間で指定してください。"
    if num_mines < 1 or num_mines >= width * height:
        return "地雷の数は1以上で、盤面サイズ未満にしてください。"
    if reveal_safe is None:
        reveal_safe = 0
    if reveal_safe < 0:
        return "ランダムに開けるマスの数は0以上で指定してください。"
    safe_cells = (width * height) - num_mines
    if reveal_safe > safe_cells:
        return f"ランダムに開けるマスの数は0から{safe_cells}の範囲で指定してください。"
    return None

def play(width, height, num_mines, reveal_safe=0):
    board = generate_minesweeper_board(width, height, num_mines)
    revealed_positions = set()
    if reveal_safe > 0:
        safe_positions = [
            (x, y)
            for y in range(height)
            for x in range(width)
            if board[y][x] != '💣'
        ]
        reveal_count = min(reveal_safe, len(safe_positions))
        revealed_positions = set(random.sample(safe_positions, reveal_count))
    return format_minesweeper_board(board, revealed_positions)

def setup(bot):
    @bot.tree.command(name="minesweeper", description="マインスイーパーをプレイ")
    @app_commands.describe(
        reveal_safe="爆弾ではないマスをランダムに開ける数（省略時は0）",
    )
    async def minesweeper_command(
        interaction: discord.Interaction,
        width: int,
        height: int,
        num_mines: int,
        reveal_safe: int = 0,
    ):
        error_message = validate_minesweeper_input(width, height, num_mines, reveal_safe)
        if error_message:
            await interaction.response.send_message(error_message, ephemeral=True)
            return
        await interaction.response.send_message(play(width, height, num_mines, reveal_safe))
