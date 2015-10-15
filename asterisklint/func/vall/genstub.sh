#!/bin/sh
filename="$1"; shift
cat > $filename << EOF
from ..base import FuncBase


EOF
for cmd in "$@"; do
cat >> $filename << EOF
class $cmd(FuncBase):
    pass


EOF
done
cat >> $filename << EOF
def register(func_loader):
    for func in (
EOF
for cmd in "$@"; do
cat >> $filename << EOF
            $cmd,
EOF
done
cat >> $filename << EOF
            ):
        func_loader.register(func())
EOF
