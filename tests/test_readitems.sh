#   VIM SETTINGS: {{{3
#   vim: set tabstop=4 modeline modelines=10 foldmethod=marker:
#   vim: set foldlevel=2 foldcolumn=3: 
#   }}}1
source "$HOME/._exports.sh"

echoerr() {
	echo "$@" > /dev/stderr
}

_grablabels=( "Continue" "Ongoing" "TODO" )
_dir_worklog="$mld_tasklogs/_worklog"
_dir_output="$mld_out_local"

#	Verify existance _dir_worklog, _dir_output
#	{{{
if [ ! -d "$_dir_worklog" ]; then
	echoerr "error, not found, _dir_worklog=($_dir_worklog)"
	exit 2
fi
if [ ! -d "$_dir_output" ]; then
	echoerr "error, not found, _dir_output=($_dir_output)"
	exit 2
fi
#	}}}

for loop_label in "${_grablabels[@]}"; do
	echoerr "$loop_label"
	readtaskblocks --gpgin -D "$_dir_worklog" --postfix ".worklog.vimgpg" grabitems --nokeys --label "$loop_label" > "$_dir_output/grab-$loop_label.txt"
done


echoerr "todaytasks"
readtaskblocks --gpgin -D "$_dir_worklog" --postfix ".worklog.vimgpg" todaytasks > "$_dir_output/today-tasks.txt"

