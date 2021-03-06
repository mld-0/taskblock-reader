# 	VIM SETTINGS: {{{3
# 	VIM: let g:mldvp_filecmd_open_tagbar=0 g:mldvp_filecmd_NavHeadings="" g:mldvp_filecmd_NavSubHeadings="" g:mldvp_filecmd_NavDTS=0 g:mldvp_filecmd_vimgpgSave_gotoRecent=0
# 	vim: set tabstop=4 modeline modelines=10 foldmethod=marker:
# 	vim: set foldlevel=2 foldcolumn=3: 
# 	}}}1
#	{{{2
nl=$'\n'; tab=$'\t';

#	If shtab is installed, and dtscan is installed, and user shell is zsh, then continue
if ! command -v shtab > /dev/null; then
	echo "error, shtab not found" > /dev/stderr
	exit 2
fi
if ! command -v readtaskblocks > /dev/null; then
	echo "error, dtscan not found" > /dev/stderr
	exit 2
fi
if [[ $SHELL == ".*/zsh" ]]; then
	echo "error, not zsh" > /dev/stderr
	exit 2
fi

_prog_name='readtaskblocks'
#	zsh site-functions, standard directory for completion scripts
path_sitefunctions="/usr/local/share/zsh/site-functions"

#	name of file is package name with leading '_' (as per zsh convention)
name_completefile="_$_prog_name"

echo "Create file$nl$tab$path_sitefunctions/$name_completefile" > /dev/stderr
shtab readblock.__main__._parser --shell=zsh --prog="$_prog_name" > "$path_sitefunctions/$name_completefile" 


#	}}}1


