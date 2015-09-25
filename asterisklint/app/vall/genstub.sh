#!/bin/sh
filename="$1"; shift
cat > $filename << EOF
from ..base import AppBase


EOF
for cmd in "$@"; do
cat >> $filename << EOF
class $cmd(AppBase):
    pass


EOF
done
cat >> $filename << EOF
def register(app_loader):
    for app in (
EOF
for cmd in "$@"; do
cat >> $filename << EOF
            $cmd,
EOF
done
cat >> $filename << EOF
            ):
        app_loader.register(app())
EOF
