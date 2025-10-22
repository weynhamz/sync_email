#1760877300
/usr/bin/python config_helper.py create
#1760877310
/usr/bin/python config_helper.py validate
#1760877363
/usr/bin/python test_sync.py
#1760878187
/usr/bin/python oauth2_helper.py --setup
#1760878276
/usr/bin/python sync_mail.py --config config.oauth2.example.json --dry-run
#1760878295
pip list | grep google
#1760878311
/usr/bin/python oauth2_helper.py --test
#1760878338
/usr/bin/python -m pip list | grep google
#1760878347
/usr/bin/python sync_mail.py --dry-run
#1760878392
/usr/bin/python test_oauth2.py
#1760878439
git status
#1760948245
which pip
#1760948307
git cmm 'Add Oauth2 support.'
#1760948824
chmod +x setup.sh
#1760949163
/usr/bin/python env_check.py
#1760949245
head -20 setup.sh
#1760949380
bash setup.sh
#1760949956
git cmm 'Setup venv support'
#1760950367
/usr/bin/python test_gmail_search.py
#1760950385
/usr/bin/python config_helper.py validate config.oauth2.example.json
#1760950409
/usr/bin/python sync_mail.py --help
#1760950432
/usr/bin/python sync_mail.py --config config.oauth2.example.json --dry-run --skip-venv-check
#1760950462
/usr/bin/python gmail_search_demo.py
#1760952224
timeout 20 python sync_mail.py --dry-run
#1760958942
python gmail_search_demo.py
#1760959068
python test_gmail_search.py
#1760959305
git cmm 'Support Gmail search query'
#1760960307
git add sync_mail.py
#1760960328
git cmm "Apply _TO_DELETE label for messages to be deleted"
#1760961096
git add .
#1760961106
git cmm 'Fix message check logic'
#1760961219
timeout 30 python sync_mail.py --dry-run || true
#1761008312
python sync_mail.py --dry-run
#1761008581
timeout 20 python sync_mail.py --dry-run || true
#1761008926
tail -20 /home/weynhamz/W.Weynham/Workspace/sync_mail/sync_mail.log
#1761009318
timeout 30 python sync_mail.py --dry-run | head -50
#1761009767
timeout 60 python sync_mail.py --dry-run | head -50
#1761010231
git cmm 'Remove blanking trailing spaces.'
#1761010314
git-modified-diff
#1761010527
git dfc
#1761010538
git cmm 'Apply _Migrated marker'
#1761010539
git st
#1761010540
git diff
#1761011038
timeout 30 python sync_mail.py --dry-run | head -20
#1761013989
git cmam
#1761014030
git cmm 'fixup'
#1761014225
git cmm 'fixup migrated label'
#1761014267
git cmm 'Improve MESSAGE-ID search'
#1761014274
reload_history
#1761053166
git cmm fixup
#1761053190
git cmm 'Reuse find message id logic'
#1761057016
git cmm 'Stand IMAP header first'
#1761057197
git reset HEAD~
#1761127960
git cmm 'Skip on multipe IDs result on id lookup, something is clearly wrong on Gmail side.'
#1761127964
git co .
#1761127969
git-cleangit.sh
#1761127971
git gc
#1761128460
git cmm "Save Github Copilot Chat conversation"
#1761128962
history
#1761129780
git rba
#1761129789
tig
#1761129812
git rbi ecd52fdf1ffcd90c3d2a38903237c439b0302339
#1761129969
git co sync_mail.py
#1761129972
vim sync_mail.py
#1761129987
git rbc
#1761129997
clean_history
#1761130007
vim $HOME/.bash_history
#1761130028
vim $HISTFILE
