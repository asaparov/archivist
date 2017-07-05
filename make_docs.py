import os
from shutil import copyfile
import xml.etree.ElementTree as et
from io import StringIO

header_file = 'header.html'
footer_file = 'footer.html'
style_file = 'style.css'
script_file = 'script.js'
src_root = os.path.abspath('../') + os.path.sep
url_root = 'http://asaparov.org/docs/'
source_file_url = 'https://github.com/asaparov/{0}/blob/master/{1}'
source_line_url = 'https://github.com/asaparov/{0}/blob/master/{1}#L{2}'
source_block_url = 'https://github.com/asaparov/{0}/blob/master/{1}#L{2}-L{3}'
refs = {}	# this map stores all refid's


def get_path(path):
	if path.find(src_root) != 0:
		raise ValueError('Given filepath does not begin with source prefix.')
	return path[len(src_root):]

class Location:
	def __init__(self, path, start, end):
		self.path = get_path(path)
		self.start = start
		self.end = end if end != -1 else None

def get_file_link(sundered_path):
	return source_file_url.format(sundered_path[0], '/'.join(sundered_path[1:]))

def get_source_link(location):
	sundered = os_path_sunder(location.path)
	if location.end == None:
		return source_line_url.format(sundered[0], '/'.join(sundered[1:]), location.start)
	else:
		return source_block_url.format(sundered[0], '/'.join(sundered[1:]), location.start, location.end)

class Variable:
	def __init__(self, type, name, description, initializer, location):
		self.type = type
		self.name = name
		self.description = description
		self.initializer = initializer
		self.location = location
		self.link = None

class Typedef:
	def __init__(self, type, name, args, description, location):
		self.type = type
		self.name = name
		self.args = args
		self.description = description
		self.location = location
		self.link = None

class TemplateParam:
	def __init__(self, type, default_value):
		self.type = type
		self.default_value = default_value

class FunctionParam:
	def __init__(self, type, name, name_text, default_value):
		self.type = type
		self.name = name
		self.name_text = name_text
		self.default_value = default_value

	def to_html(self):
		string = to_html(self.type) + ' ' + self.name
		if self.default_value != None:
			string += ' = ' + self.default_value
		return string

	def to_text(self):
		string = to_text(self.type) + ' ' + self.name_text
		if self.default_value != None:
			string += ' = ' + self.default_value
		return string

class ParamDescription:
	def __init__(self, name, description):
		self.name = name
		self.description = description

class Function:
	def __init__(self, type, name, is_static, is_const, templates, args, description, template_descriptions, arg_descriptions, location):
		self.type = type
		if name.find('operator') == 0:
			name = 'operator ' + name[len('operator'):]
		self.name = name
		self.is_static = is_static
		self.is_const = is_const
		self.templates = templates
		self.args = args
		self.description = description
		self.template_descriptions = template_descriptions
		self.arg_descriptions = arg_descriptions
		self.location = location
		self.link = None

class Class:
	def __init__(self, name, namespace, templates, description, template_descriptions, objects, location):
		self.name = name
		self.namespace = namespace
		self.templates = templates
		self.description = description
		self.template_descriptions = template_descriptions
		self.objects = objects
		self.location = location
		self.link = None

class File:
	def __init__(self):
		self.description = None
		self.objects = []
		self.link = None

def parse_variable(member):
	type = member.find('type')
	name = member.find('name').text
	description = member.find('detaileddescription')
	initializer_element = member.find('initializer')
	initializer = initializer_element.text if initializer_element != None else None
	location_attrib = member.find('location').attrib
	if 'bodyfile' in location_attrib:
		location = Location(location_attrib['bodyfile'], int(location_attrib['bodystart']), None)
	else:
		location = Location(location_attrib['file'], int(location_attrib['line']), None)
	variable = Variable(type, name, description, initializer, location)
	if 'id' in member.attrib:
		refs[member.attrib['id']] = variable
	return variable

def parse_typedef(member):
	type = member.find('type')
	name = member.find('name').text
	args = member.find('argsstring')
	description = member.find('detaileddescription')
	location_attrib = member.find('location').attrib
	location = Location(location_attrib['bodyfile'], int(location_attrib['bodystart']), None)
	typedef = Typedef(type, name, args, description, location)
	if 'id' in member.attrib:
		refs[member.attrib['id']] = typedef
	return typedef

def sp_to_spaces(element):
	children = list(element)
	if element.text == None:
		element.text = ''
	last = None
	for child in children:
		if child.tag == 'sp':
			str = ' ' + (child.text if child.text != None else '') + (child.tail if child.tail != None else '')
			if last == None:
				element.text += str
			else:
				last.tail += str
			element.remove(child)
		else:
			sp_to_spaces(child)
			last = child
			if last.tail == None:
				last.tail = ''

def to_html(element):
	# convert all XML tags into HTML tags, without changing the tree structure
	parameter_lists, codelines, headings, tables, simplesects = [], [], [], [], {}
	for child in element.iter():
		if child.tag == 'para':
			child.tag = 'p'
		elif child.tag == 'emphasis':
			child.tag = 'i'
		elif child.tag == 'bold':
			child.tag = 'b'
		elif child.tag == 'computeroutput':
			child.tag = 'code'
		elif child.tag == 'linebreak':
			child.tag = 'br'
		elif child.tag == 'ulink':
			child.tag = 'a'
			link = child.attrib['url']
			child.attrib.clear()
			child.attrib['href'] = link
		elif child.tag == 'ref':
			ref = child.attrib['refid']
			if ref in refs:
				obj = refs[ref]
				if isinstance(obj, File):
					child.tag = 'a'
					child.attrib.clear()
					child.attrib['href'] = obj.link
				elif obj.link != None:
					child.tag = 'a'
					child.attrib.clear()
					child.attrib['href'] = url_root + obj.location.path + '.html#' + obj.link
		elif child.tag == 'parameterlist':
			child.tag = 'table'
			child.attrib['class'] = 'params'
			parameter_lists.append(child)
		elif child.tag == 'parameteritem':
			child.tag = 'tr'
		elif child.tag == 'parameternamelist':
			text = to_text(child)
			child.clear()
			child.tag = 'td'
			child.attrib['class'] = 'paraminfoname'
			child.text = text
		elif child.tag == 'parameterdescription':
			child.tag = 'td'
		elif child.tag == 'simplesect':
			kind = child.attrib['kind']
			if kind not in simplesects:
				simplesects[kind] = []
			simplesects[kind].append(child)
		elif child.tag == 'orderedlist':
			child.tag = 'ol'
		elif child.tag == 'itemizedlist':
			child.tag = 'ul'
		elif child.tag == 'listitem':
			child.tag = 'li'
		elif child.tag == 'programlisting':
			child.tag = 'pre'
			child.attrib['class'] = 'codeblock'
		elif child.tag == 'codeline':
			child.tag = 'span'
			child.attrib['class'] = 'codeline'
			codelines.append(child)
		elif child.tag == 'highlight':
			child.tag = 'span'
			child.attrib['class'] = 'highlight ' + child.attrib['class']
		elif child.tag == 'heading':
			headings.append(child)
		elif child.tag == 'formula':
			if child.text.strip().startswith('\\['):
				child.tag = 'div'
			else:
				child.tag = 'span'
			child.attrib.clear()
			child.attrib['class'] = 'formula'
		elif child.tag == 'table':
			tables.append(child)
		elif child.tag == 'row':
			child.tag = 'tr'
		elif child.tag == 'entry':
			child.tag = 'td'
			is_head = False
			if 'thead' in child.attrib and child.attrib['thead'] == 'yes':
				is_head = True
			child.attrib.clear();
			if is_head:
				child.attrib['class'] = 'thead'

	# transform the parameter list into a table, move all children into a tbody node
	for node in parameter_lists:
		children = list(node)
		tbody = et.Element('tbody')
		title = et.SubElement(tbody, 'th', {'colspan':'2', 'class':'paramtitle'})
		if node.attrib['kind'] == 'templateparam':
			title.text = 'Template parameters'
			node.clear()
			node.attrib['class'] = 'tparams'
		else:
			title.text = 'Parameters'
			node.clear()
			node.attrib['class'] = 'params'

		for child in children:
			tbody.append(child)
		node.append(tbody)

	# put tables in a div to enable overflow
	for table in tables:
		children = list(table)
		new_table = et.Element('table')
		new_table.attrib['class'] = 'table table-striped table-bordered'
		for child in children:
			new_table.append(child)
		table.clear()
		table.append(new_table)

		table.tag = 'div'
		table.attrib['class'] = 'table-wrapper'

	# transform headings and generate anchors
	for heading in headings:
		heading.tag = 'h' + heading.attrib['level']
		heading.attrib.clear()
		anchor = et.SubElement(heading, 'a', {'id':heading.text.strip().replace(' ','-').lower()})
		anchor.tail = heading.text
		heading.text = ''

	for kind,sections in simplesects.items():
		parent = element[0]

		first = sections[0]
		children = list(first)
		first.clear()
		first.tag = 'div'
		first.attrib['class'] = kind + 's'
		title = et.SubElement(first, 'span', {'class':'returntitle'})
		if kind == 'return':
			title.text = 'Returns'
		elif kind == 'see':
			title.text = 'See'
		first_return = et.SubElement(first, 'span', {'class':'return'})
		for child in children:
			first_return.append(child)

		for other in sections[1:]:
			other.tag = 'span'
			other.attrib['class'] = kind
			parent.remove(other)
			first.append(other)

	for codeline in codelines:
		sp_to_spaces(codeline)

	str = element.text if element.text != None else ''
	str += ''.join([et.tostring(child, encoding='utf-8', method='html').decode('utf-8') for child in element])
	return str.strip()

def to_text(element):
	str = ''
	for child in element.itertext():
		str += child
	return str.strip()

def parse_function(member):
	templates, args, template_descriptions, arg_descriptions = [], [], [], []
	return_type = member.find('type')
	is_static = (member.attrib['static'] == 'yes')
	is_const = (member.attrib['const'] == 'yes')
	function_name = member.find('name').text
	function_description = member.find('detaileddescription')
	location_attrib = member.find('location').attrib
	if 'bodyfile' in location_attrib:
		location = Location(location_attrib['bodyfile'], int(location_attrib['bodystart']), int(location_attrib['bodyend']))
	else:
		location = Location(location_attrib['file'], int(location_attrib['line']), None)
	for template_param in member.findall('templateparamlist/param'):
		type = template_param.find('type').text
		declname_element = template_param.find('declname')
		type += ' '+declname_element.text if declname_element != None else ''
		default_value_element = template_param.find('defval')
		default_value = default_value_element.text if default_value_element != None else None
		templates.append(TemplateParam(type, default_value))
	for template_description in member.findall('detaileddescription/parameterlist[@kind=\'templateparam\']/parameteritem'):
		name = template_description.find('parameternamelist/parametername').text
		description = template_description.find('parameterdescription').text
		template_descriptions.append(ParamDescription(name, description))
	for arg in member.findall('param'):
		type = arg.find('type')
		name_element = arg.find('declname')
		if type == 'void' and name_element == None:
			continue
		name = name_text = name_element.text if name_element != None else ''
		array_element = arg.find('array')
		array = array_element.text if array_element != None else ''
		has_array = False
		for node in type.iter():
			if node.text == None:
				continue
			var_index = node.text.find('(&)')
			if var_index != -1:
				name_text = node.text[var_index:].replace('(&)', '(&' + name + ')' + array)
				name = node.text[var_index:].replace('(&)', '<span class="black">(&</span>' + name + '<span class="black">)' + array + '</span>')
				node.text = node.text[:var_index]
				has_array = True
				break
		if not has_array:
			name += '<span class="black">' + array + '</span>'
			name_text += array
		default_value_element = arg.find('defval')
		default_value = default_value_element.text if default_value_element != None else None
		args.append(FunctionParam(type, name, name_text, default_value))
	for arg_description in member.findall('detaileddescription/parameterlist[@kind=\'param\']/parameteritem'):
		name = template_description.find('parameternamelist/parametername').text
		description = template_description.find('parameterdescription').text
		arg_descriptions.append(ParamDescription(name, description))
	function = Function(return_type, function_name, is_static, is_const, templates, args, function_description, template_descriptions, arg_descriptions, location)
	if 'id' in member.attrib:
		refs[member.attrib['id']] = function
	return function

def parse_compound_name(compound_name):
	i = compound_name.find('<')
	simple = compound_name[:i] if i != -1 else compound_name
	tokens = simple.split('::')
	name = tokens[-1] + (compound_name[i:] if i != -1 else '')
	namespace = '::'.join(tokens[:-1])
	return name, namespace

def parse_class(ref):
	tree = et.parse(os.path.sep.join(['Docs','xml', ref + '.xml']))
	templates, template_descriptions, objects = [], [], []

	name, namespace = parse_compound_name(tree.find('compounddef/compoundname').text)
	description_element = tree.find('compounddef/detaileddescription')
	class_description = description_element
	location_attrib = tree.find('compounddef/location').attrib
	location = Location(location_attrib['bodyfile'], int(location_attrib['bodystart']), int(location_attrib['bodyend']))
	for template_param in tree.findall('compounddef/templateparamlist/param'):
		type = template_param.find('type').text
		declname_element = template_param.find('declname')
		type += ' '+declname_element.text if declname_element != None else ''
		default_value_element = template_param.find('defval')
		default_value = default_value_element.text if default_value_element != None else None
		templates.append(TemplateParam(type, default_value))
	for template_description in description_element.findall('parameterlist/parameteritem'):
		name = template_description.find('parameternamelist/parametername').text
		description = template_description.find('parameterdescription').text
		template_descriptions.append(ParamDescription(name, description))
	for member in tree.findall('compounddef/sectiondef[@kind=\'public-attrib\']/memberdef'):
		objects.append(parse_variable(member))
	for member in tree.findall('compounddef/sectiondef[@kind=\'public-func\']/memberdef'):
		objects.append(parse_function(member))
	for member in tree.findall('compounddef/sectiondef[@kind=\'public-static-func\']/memberdef'):
		objects.append(parse_function(member))
	for member in tree.findall('compounddef/sectiondef[@kind=\'public-type\']/memberdef'):
		objects.append(parse_typedef(member))
	cls = Class(name, namespace, templates, class_description, template_descriptions, objects, location)
	refs[ref] = cls
	return cls

def add_to_file(obj, files):
	if obj.location.path not in files:
		files[obj.location.path] = File()
	files[obj.location.path].objects.append(obj)

def parse_file(file_ref, files):
	tree = et.parse(os.path.sep.join(['Docs','xml', file_ref + '.xml']))
	path = get_path(tree.find('compounddef/location').attrib['file'])
	if path not in files:
		files[path] = File()
	file = files[path]
	refs[file_ref] = file

	# read per-file comments
	description_element = tree.find('compounddef/detaileddescription')
	if description_element != None:
		file.description = description_element

	for member in tree.findall('compounddef/sectiondef/memberdef'):
		if member.attrib['kind'] == 'function':
			file.objects.append(parse_function(member))
		elif member.attrib['kind'] == 'variable':
			file.objects.append(parse_variable(member))
		elif member.attrib['kind'] == 'typedef':
			file.objects.append(parse_typedef(member))
		elif member.attrib['kind'] == 'define':
			file.objects.append(parse_variable(member))

def parse_readme(page_ref):
	tree = et.parse(os.path.sep.join(['Docs','xml', page_ref + '.xml']))
	return tree.find('compounddef/detaileddescription')

def parse_namespace(namespace_ref, files):
	tree = et.parse(os.path.sep.join(['Docs','xml', namespace_ref + '.xml']))
	for member in tree.findall('compounddef/sectiondef/memberdef'):
		if member.attrib['kind'] == 'function':
			add_to_file(parse_function(member), files)
		elif member.attrib['kind'] == 'variable':
			add_to_file(parse_variable(member), files)
		elif member.attrib['kind'] == 'typedef':
			add_to_file(parse_typedef(member), files)
		elif member.attrib['kind'] == 'define':
			add_to_file(parse_variable(member), files)

def parse_index(files):
	tree = et.parse(os.path.sep.join(['Docs','xml','index.xml']))
	for file in tree.findall('compound[@kind=\'file\']'):
		parse_file(file.attrib['refid'], files)
	for namespace in tree.findall('compound[@kind=\'namespace\']'):
		parse_namespace(namespace.attrib['refid'], files)
	for struct in tree.findall('compound[@kind=\'struct\']'):
		add_to_file(parse_class(struct.attrib['refid']), files)
	for page in tree.findall('compound[@kind=\'page\']'):
		filename = page.find('name').text
		if filename.find('md_') == 0:
			filename = get_path(filename[3:].replace('_', os.path.sep) + '.md')
			files[filename] = File()
			files[filename].description = parse_readme(page.attrib['refid'])

def is_visible(member):
	if isinstance(member, Class):
		return has_visible(member.objects) or len(member.description) > 0
	return len(member.description) > 0

def has_visible(members):
	for member in members:
		if is_visible(member):
			return True
	return False

def get_link(obj, name_prefix=""):
	if isinstance(obj, Class):
		return 'struct ' + name_prefix + obj.name
	elif isinstance(obj, Function):
		type = obj.type if obj.type != None else ''
		args = ','.join(arg.to_text() for arg in obj.args)
		const = ' const' if obj.is_const else ''
		return to_text(type) + ' ' + name_prefix + obj.name + '(' + args + ')' + const
	elif isinstance(obj, Variable):
		type = '#define' if obj.type == None else to_text(obj.type)
		return type + ' ' + name_prefix + obj.name
	elif isinstance(obj, Typedef):
		return 'typedef ' + to_text(obj.type) + ' ' + name_prefix + obj.name + to_text(obj.args);

def compute_links(members, name_prefix=""):
	for obj in members:
		if not is_visible(obj):
			continue
		obj.link = get_link(obj, name_prefix)
		if isinstance(obj, Class):
			compute_links(obj.objects, obj.name + "::")

def generate_member_table(out, name, nav, members, title, name_prefix=""):
	link = 'table_' + name_prefix
	if name is None:
		nav.write('<li><a class="active" href="#' + link + '">File contents</a></li>')
	else:
		nav.write('<li><a href="#' + link + '">Members</a></li>')
	out.write('<a id="' + link + '"></a>')
	out.write('<table class="table members"><colgroup><col class="type-col" /><col class="name-col" /></colgroup><thead><tr><th colspan="2">' + title + '</th></tr></thead><tbody>')
	for obj in members:
		left, right = '', ''
		if not is_visible(obj):
			continue
		if isinstance(obj, Class):
			left += 'struct'
			right += '<a href="#' + obj.link + '"><b>' + obj.name + '</b></a>'
		elif isinstance(obj, Function):
			left += 'static ' if obj.is_static else ''
			left += to_html(obj.type) if obj.type != None else ''
			right += '<a href="#' + obj.link + '"><b>' + obj.name + '</b></a> ('
			right += ', '.join(['<span class="arg">'+arg.to_html()+'</span>' for arg in obj.args]) + ')'
			right += ' const' if obj.is_const else ''
		elif isinstance(obj, Variable):
			left += '#define' if obj.type == None else to_html(obj.type)
			right += '<a href="#' + obj.link + '"><b>' + obj.name + '</b></a>'
		elif isinstance(obj, Typedef):
			left += 'typedef'
			type = to_html(obj.type)
			index = type.find('()')
			right += (type[:(index+1)] if (index != -1) else to_html(obj.type)+' ')
			right += '<a href="#' + obj.link + '"><b>' + obj.name + '</b></a>'
			if index != -1:
				right += type[(index+1):] + to_html(obj.args)
		out.write('<tr class="active"><td class="type-col">' + left + '</td><td class="name-col">' + right + '</td></tr>')
	out.write('</tbody></table>')

def templates_to_html(templates):
	if len(templates) == 0:
		return ''

	params = []
	for template in templates:
		if 'enable_if' in template.type:
			continue
		param = template.type.replace('<','&lt;').replace('>','&gt;')
		if template.default_value != None:
			if template.default_value == 'void':
				continue
			param += ' = ' + template.default_value
		params.append('<span class="arg">' + param + '</span>')
	return '<div class="template">template&lt;' + ', '.join(params) + '&gt;</div>'

def generate_member_list(out, nav, members, name_prefix=""):
	for obj in members:
		if not is_visible(obj):
			continue
		out.write('<a id="' + obj.link + '"></a>')
		source_link = get_source_link(obj.location)
		if isinstance(obj, Class):
			nav.write('<li><a href="#' + obj.link + '">struct ' + obj.name + '</a>')
			out.write('<div class="panel panel-default active"><h2>struct ' + obj.name)
			out.write('<div class="source">[<a href="' + source_link + '">view source</a>]</div></h2>')
			out.write(templates_to_html(obj.templates))
			if len(obj.description) > 0:
				out.write('<p>' + to_html(obj.description) + '</p>')
			if has_visible(obj.objects):
				nav.write('<ul>')
				namespace = name_prefix + obj.name + "::"
				generate_member_table(out, obj.name, nav, obj.objects, 'Public members', namespace)
				generate_member_list(out, nav, obj.objects, namespace)
				nav.write('</ul>')
			nav.write('</li>')
			out.write('</div>')
		elif isinstance(obj, Typedef):
			typedef = to_html(obj.type)
			if '()' in typedef:
				typedef = typedef.replace('()', '(' + name_prefix + obj.name + ')') + to_html(obj.args)
			else:
				typedef += ' ' + name_prefix + obj.name
			nav.write('<li><a href="#' + obj.link + '">typedef ' + obj.name + '</a>')
			out.write('<div class="panel panel-default active"><div class="panel-heading">typedef ')
			out.write(typedef + '<div class="source">[<a href="' + source_link + '">view source</a>]</div></div><div class="panel-body">')
			out.write(to_html(obj.description))
			nav.write('</li>')
			out.write('</div></div>')
		else:
			if obj.type == None:
				type = '#define' if isinstance(obj, Variable) else ''
				type_text = type
			else:
				type = to_html(obj.type)
				type_text = to_text(obj.type)
			if isinstance(obj, Function) and obj.is_static:
				type = 'static ' + type
				type_text = 'static ' + type_text
			nav.write('<li><a href="#' + obj.link + '">' + ('' if isinstance(obj, Variable) else type_text) + ' ' + obj.name)
			out.write('<div class="panel panel-default active"><div class="panel-heading">')
			out.write('<div class="source">[<a href="' + source_link + '">view source</a>]</div>')
			if isinstance(obj, Function):
				out.write(templates_to_html(obj.templates))
			out.write(type + ' ' + name_prefix + obj.name)
			if isinstance(obj, Function):
				if obj.name.find('operator') == 0:
					nav.write(' ')
					out.write(' ')
				if len(obj.args) == 0:
					nav.write('()')
					out.write('()')
				else:
					nav.write('( ' + ', '.join(['<span class="arg">'+to_text(arg.type)+'</span>' for arg in obj.args]) + ')')
					out.write('(<table class="memname params"><tbody>')
					for arg in obj.args[:-1]:
						default = ' = '+arg.default_value if arg.default_value != None else ''
						out.write('<tr><td class="paramtype">' + to_html(arg.type) + '</td><td class="paramname">' + arg.name + '<span class="black">' + default + ',</span></td></tr>')
					default = '<span class="black"> = '+obj.args[-1].default_value+'</span>' if obj.args[-1].default_value != None else ''
					const = ' const' if obj.is_const else ''
					out.write('<tr><td class="paramtype">' + to_html(obj.args[-1].type) + '</td><td class="paramname">' + obj.args[-1].name + default + '</td><td>)' + const + '</td></tr>')
					out.write('</tbody></table>')
			elif isinstance(obj, Variable):
				if obj.initializer != None:
					out.write(' ' + obj.initializer)
			nav.write('</a></li>')
			out.write('</div><div class="panel-body">')
			out.write(to_html(obj.description))
			out.write('</div></div>')

def generate_left_nav(out, path, current_sundered_path):
	on_path = (current_sundered_path != None)
	for key in sorted(path.children.keys()):
		child_path = path.children[key]
		child_on_path = on_path and (current_sundered_path[0] == key)
		if not child_path.is_file():
			# this is a directory
			toggler_style = 'tree-toggler' if child_path.is_visible else 'invisible tree-toggler'
			toggler = '<label class="' + toggler_style + '">' + ('-' if child_on_path else '+') + '</label>'
			tree_ul = ('<ul class="tree"' + (' style="display:none"' if not child_on_path else '') + '>') if True else ''
			if 'README.md' in child_path.children:
				child = child_path.children['README.md']
				if child_on_path and current_sundered_path[1] == 'README.md':
					out.write('<li><div class="toc_item active">' + toggler + key + '</div>' + tree_ul)
				else:
					link = url_root + os.path.split(child_path.children['README.md'].object)[0] + '/index.html'
					out.write('<li><div class="toc_item">' + toggler + '<a href="' + link + '">' + key + '</a></div>' + tree_ul)
			else:
				out.write('<li><div class="toc_item">' + toggler + key + '</div>' + tree_ul)
			generate_left_nav(out, child_path, current_sundered_path[1:] if (on_path and child_on_path) else None)
			out.write('</ul></li>')
		else:
			# this is a file
			if child_path.object == None or not child_path.is_visible:
				continue
			if child_on_path:
				out.write('<li class="toc_item active">' + key + '</li>')
			else:
				link = child_path.object + '.html'
				out.write('<li class="toc_item"><a href="' + url_root + link + '">' + key + '</a></li>')

def generate_right_nav(out, nav, members):
	out.write('<nav id="rightnav">' + nav.getvalue() + '</nav>')

# see: https://stackoverflow.com/questions/4579908/cross-platform-splitting-of-path-in-python
def os_path_sunder(path):
	parts = []
	while True:
		newpath, tail = os.path.split(path)
		if newpath == path:
			assert not tail
			if path: parts.append(path)
			break
		parts.append(tail)
		path = newpath
	parts.reverse()
	return parts

class Path:
	def __init__(self, is_file, object, is_visible = False):
		self.children = (None if is_file else {})
		self.object = object
		self.is_visible = is_visible

	def is_file(self):
		return self.children == None

	def add(self, path, object, is_visible):
		if is_visible:
			self.is_visible = True
		if len(path) == 1:
			self.children[path[0]] = Path(True, object, is_visible)
			return
		elif path[0] not in self.children:
			self.children[path[0]] = Path(False, None, is_visible)
		self.children[path[0]].add(path[1:], object, is_visible)

	def get(self, path):
		if len(path) == 1:
			return self.children[path[0]]
		else:
			return self.children[path[0]].get(path[1:])

# read the header and footer files
with open(header_file, 'r') as f:
	header = f.read()
	header = header.replace('$style_file', url_root + style_file)
with open(footer_file, 'r') as f:
	footer = f.read()
	footer = footer.replace('$script_file', url_root + script_file)

# read 'index.xml'
files = {}
parse_index(files)

# sort objects in each file by line number, and construct the path tree structure
root = Path(False, None)
for key, value in files.items():
	value.objects.sort(key=lambda obj : obj.location.start)
	compute_links(value.objects)
	value.link = url_root + key + '.html'
	root.add(os_path_sunder(key), key, has_visible(value.objects))

# generate html output
for key, value in files.items():
	sundered = os_path_sunder(key)
	directory, filename = os.path.split(key)
	if filename == 'README.md' and len(value.description) > 0:
		filepath = os.path.sep.join([directory, 'index'])
	elif not has_visible(value.objects):
		continue
	else:
		filepath = os.path.sep.join([directory, filename])

	filepath = os.path.sep.join(['Docs', 'html', filepath + '.html'])
	os.makedirs(os.path.dirname(filepath), exist_ok=True)
	out = open(filepath, 'w')
	out.write(header.replace('$title', key + ' Documentation').replace('$navbar_title', sundered[0] + ' Documentation'))

	out.write('<nav id="leftnav"><div id="menu"><ul>')
	generate_left_nav(out, root, sundered)
	out.write('</ul></div></nav>')

	out.write('<div id="container">')
	title = filename if filename != 'README.md' else sundered[0]
	out.write('<div class="title h1">' + title)
	if filename != 'README.md':
		out.write('<div class="source">[<a href="' + get_file_link(sundered) + '">view source</a>]</div>')
	out.write('</div><div id="embedded_nav"></div>')

	if value.description != None:
		out.write(to_html(value.description))

	# generate the summary table
	nav = StringIO()
	nav.write('<div id="toc"><div id="toc_title"><b>Table of contents</b></div><ul>')
	if filename != 'README.md':
		generate_member_table(out, None, nav, value.objects, 'Classes, functions, and variables in this file')

	# generate detailed entries for each object in the file
	generate_member_list(out, nav, value.objects)

	out.write('</div>')
	nav.write('</ul></div>')
	generate_right_nav(out, nav, value.objects)
	if filename == 'README.md':
		# for README.md files, hide the table of contents
		out.write('<style>#embedded_nav {width:0;height:0;padding:0;overflow:hidden;} #rightnav {width:0;height:0;padding:0;}</style>')
	out.write(footer)
	nav.close()
	out.close()

copyfile(style_file, os.path.sep.join(['Docs','html', style_file]))
copyfile(script_file, os.path.sep.join(['Docs','html', script_file]))
