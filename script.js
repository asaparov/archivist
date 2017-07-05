navbar = $('#header');
leftnav = $('#leftnav');
rightnav = $('#rightnav');
contents = $('#container');
embedded_nav = $('#embedded_nav')
menu = $('#menu');
toc = $('#toc');
overlay = $('#overlay');
sidebar = $('#sidebar');
footer = $('#footer');

/* see: http://jsfiddle.net/mekwall/up4nu/ */
navs = rightnav.find('a');
anchors = navs.map(function() {
	return $('a[id^="' + $(this).attr('href').substring(1) + '"]');
});
is_nav_embedded = false;
is_collapsed = false;

max_width = parseInt(contents.css('max-width'));
leftnav_width = parseInt(leftnav.css('width'));
rightnav_width = parseInt(rightnav.css('width'));
toc_width = parseInt(toc.css('width'));
nav_margin = 35;
min_pad = 20;
threshold = 780;

offset = 0
if (anchors.length > 0)
	offset = -anchors[0].offset().top;
prev_nav = 0;
scrolling = true;

function update_navs(scroll) {
	doc_width = $(window).width();
	doc_height = $(window).height();
	width = Math.min(max_width, doc_width - 2 * (min_pad + nav_margin) - leftnav_width - rightnav_width);
	left = Math.max(Math.min((doc_width - width) / 2, doc_width - width - nav_margin - rightnav_width - min_pad), min_pad + leftnav_width + nav_margin);

	if (doc_width < threshold) {
		if (!is_nav_embedded) {
			toc.detach().appendTo(embedded_nav);
			toc.css('width', 'auto');
			rightnav.css('display', 'none');
			is_nav_embedded = true;
		} if (!is_collapsed) {
			menu.detach().appendTo(sidebar);
			navbar.css('display', 'block');
			leftnav.css('display', 'none');
			contents.css('margin-top', '65px');
			is_collapsed = true;
		}
		width = doc_width - 2 * min_pad;
		left = min_pad;
	} else if (width < max_width - nav_margin - rightnav_width) {
		if (!is_nav_embedded) {
			toc.detach().appendTo(embedded_nav);
			toc.css('width', 'auto');
			rightnav.css('display', 'none');
			is_nav_embedded = true;
		} if (is_collapsed) {
			menu.detach().appendTo(leftnav);
			navbar.css('display', 'none');
			leftnav.css('display', 'block');
			contents.css('margin-top', 0);
			is_collapsed = false;
		}
		width = doc_width - 2 * min_pad - nav_margin - leftnav_width;
	} else {
		if (is_nav_embedded) {
			toc.detach().appendTo(rightnav);
			toc.css('width', toc_width);
			rightnav.css('display', 'block');
			is_nav_embedded = false;
		} if (is_collapsed) {
			menu.detach().appendTo(leftnav);
			navbar.css('display', 'none');
			leftnav.css('display', 'block');
			contents.css('margin-top', 0);
			is_collapsed = false;
		}
	}

	leftnav_x = left - nav_margin - leftnav_width;
	if (leftnav_x <= min_pad) {
		leftnav.css('left', min_pad);
		rightnav.css('left', leftnav_width + min_pad + width + 2 * nav_margin);
		contents.css('width', width);
		contents.css('margin-left', leftnav_width + nav_margin + min_pad);
	} else {
		leftnav.css('left', leftnav_x);
		rightnav.css('left', left + width + nav_margin);
		contents.css('width', max_width);
		contents.css('margin-left', 'auto');
	}
	contents.css('margin-left', left);
	update_nav_height(doc_height, scroll);
}

function update_nav_height(doc_height, scroll) {
	nav_height = Math.min(footer.offset().top - scroll, doc_height - 5);
	leftnav.css('max-height', nav_height - 60);
	rightnav.css('max-height', nav_height - 60);
}

$(window).resize(function() {
	scroll = $(window).scrollTop();
	update_navs(scroll);
	scrolling = false;
	if (anchors.length > 0)
		$(this).scrollTop(anchors[prev_nav].offset().top + offset);
	else $(this).scrollTop(offset);
	scrolling = true;
});

$(window).scroll(function() {
	if (!scrolling) return;

	i = 0;
	scroll = $(window).scrollTop();
	for (; i < anchors.length; i++) {
		if (scroll + 1 < anchors[i].offset().top) break;
	}
	i = Math.max(i - 1, 0);
	if (anchors.length > 0)
		offset = scroll - anchors[i].offset().top;
	else offset = scroll;

	if (i != prev_nav) {
		$(navs[prev_nav]).removeClass('active');
		$(navs[i]).addClass('active');
		prev_nav = i;
	}

	update_nav_height($(window).height(), scroll);
});

$('label.tree-toggler').click(function () {
	if ($(this).text() == '+')
		$(this).text('-');
	else $(this).text('+');
	$(this).parent().parent().children('ul.tree').toggle(300);
});

$('[data-toggle="openmenu"]').click(function () {
	overlay.css('z-index', 999);
	sidebar.addClass('toggled');
	overlay.addClass('toggled');
});

$('[data-toggle="closemenu"]').click(function () {
	sidebar.removeClass('toggled');
	overlay.removeClass('toggled');
	setTimeout(function(){ overlay.css('z-index', -1000); }, 500);
});

scroll = $(window).scrollTop();
update_navs(scroll);
if (!is_collapsed)
	leftnav.css('display', 'block');
if (!is_nav_embedded)
	rightnav.css('display', 'block');
