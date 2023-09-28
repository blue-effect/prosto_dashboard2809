import Tags from "./tags.js"

Tags.init('#select-channels', {
	'clearEnd': true,
	'allowClear': true
})

Tags.init('#select-programs', {
	'server': '/titles',
	'liveServer': true,
	'labelField': 'name',
	'valueField': 'name',
	'debounceTime': 500
})