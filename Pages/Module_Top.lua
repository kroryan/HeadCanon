-- <nowiki>

-------------------------------------------------------------------------------
--                              Module:Top
--
-- This module renders the icons in the top-right corner of articles.
-- It also formats the page title with {{DISPLAYTITLE}}. It is a rewrite of
-- [[Template:Top]].
-------------------------------------------------------------------------------

local DEBUG_MODE = false -- if true, errors are not caught

-------------------------------------------------------------------------------
-- Icon data
-------------------------------------------------------------------------------

--[[
-- This table stores data for all the icons displayed in the top-right. It can
-- have the following fields:
-- * image - the icon image name, minus any "File:" prefix (required).
-- * tooltip - the icon tooltip (optional).
-- * link - the page to link from the icon (optional).
-- * category - a category to go with the icon, minus any "Category:" prefix
--     (optional).
-- * protectionAction - for protection icons, an action such as "edit" or "move"
--     to check (optional).
-- * protectionLevel - for protection icons, the protection level to check,
--     such as "sysop". If the page doesn't have the right protection level
--     it is put in a tracking category and the icon is not displayed
--     (optional).
-- Note: this is just a convenient place to store the data. The subtables are
-- accessed from the code manually, so adding new subtables won't automatically
-- add new icons, and removing subtables may break things.
--]]

local iconData = {
	btr = {
		image = "Era-icon-btr.png",
		tooltip = "The subject of this article appeared before the Republic.",
		link = "Pre-Republic era",
		category = "Pre-Republic era articles"
	},
	old = {
		image = "Era-icon-old.png",
		tooltip = "The subject of this article appeared in the Old Republic era.",
		link = "Old Republic era",
		category = "Old Republic era articles"
	},
	gpr = {
		image = "Era-icon-gpr.png",
		tooltip = "The subject of this article appeared in the Great Peace of the Republic.",
		link = "Great Peace of the Republic",
		category = "Great Peace of the Republic articles"
	},
	tcw = {
		image = "Era-icon-tcw.png",
		tooltip = "The subject of this article appeared during the Clone Wars.",
		link = "Clone Wars",
		category = "Clone Wars articles"
	},
	imp = {
		image = "Era-icon-imp.png",
		tooltip = "The subject of this article appeared in the Imperial Period.",
		link = "Imperial Period",
		category = "Imperial Period articles"
	},
	reb = {
		image = "Era-icon-reb.png",
		tooltip = "The subject of this article appeared in the Rebellion era.",
		link = "Rebellion era",
		category = "Rebellion era articles"
	},
	new = {
		image = "Era-icon-new.png",
		tooltip = "The subject of this article appeared in the New Republic era.",
		link = "New Republic era",
		category = "New Republic era articles"
	},
	njo = {
		image = "Era-icon-njo.png",
		tooltip = "The subject of this article appeared in the New Jedi Order era.",
		link = "New Jedi Order era",
		category = "New Jedi Order era articles"
	},
	leg = {
		image = "Era-icon-leg.png",
		tooltip = "The subject of this article appeared in the Legacy era.",
		link = "Legacy era",
		category = "Legacy era articles"
	}
}

-------------------------------------------------------------------------------
-- Helper functions
-------------------------------------------------------------------------------

-- Find whether the specified page exists. We use pcall to catch errors if we
-- are over the expensive parser function count limit, or a number of other
-- juicy errors. This function increases the expensive parser function count
-- for every new page called.
local function exists(page)
	local success, title = pcall(mw.title.new, page)
	return success and title and title.exists or false
end

-------------------------------------------------------------------------------
-- Eras class
-------------------------------------------------------------------------------

-- The eras class does all of the heavy lifting in the module. We use a class
-- rather than normal functions so that we can avoid passing lots of different
-- values around for each different function.

local Eras = {}
Eras.__index = Eras -- Set up inheritance for tables that use Eras as a metatable.

-- This function makes a new eras object. Here we set all the values from the
-- arguments and do any preprocessing that we need.
function Eras.new(args, title)
	local obj = setmetatable({}, Eras) -- Make our object inherit from Eras.
	obj.title = title or mw.title.getCurrentTitle()

	-- Set object structure
	obj.categories = {}

	-- Set display title parameters
	obj.noDisplayTitle = args.notitle
	obj.displayTitleBase = args.title
	obj.displayTitleParen = args.title2

	-- Set hidden status
	obj.isHidden = args.hide
	
	-- Set notoc value
	obj.hideToc = args.notoc

	-- Get the icon data.
	do
		local icons = {}
		for _, v in ipairs(args) do
			local t = iconData[string.lower(v)]
			if t then
				icons[string.lower(v)] = t
			else
				-- The specified icon wasn't found in the icon data, so set a
				-- tracking category flag.
				obj.hasBadParameter = true
			end
		end
		obj.icons = icons
	end

	return obj
end

-- Raise an error. If DEBUG_MODE is set to false, then errors raised here
-- are caught by the export function p._main.
function Eras:raiseError(msg)
	local level
	if DEBUG_MODE then
		level = nil
	else
		level = 0 -- Suppress module name and line number in the error message.
	end
	error(msg, level)
end

-- Add a category, to be rendered at the very end of the template output.
function Eras:addCategory(cat, sort)
	table.insert(self.categories, {category = cat, sortKey = sort})
end

-- Shortcut method for getting an icon data subtable.
function Eras:getIconData(code)
	return self.icons[code]
end

-- Returns a boolean showing whether any of the icons were specified by the
-- user.
function Eras:hasAnyOfIcons(...)
	for i = 1, select('#', ...) do
		if self:getIconData(select(i, ...)) then
			return true
		end
	end
	return false
end	

-- Analyses the page name and sets {{DISPLAYTITLE}}.
function Eras:renderDisplayTitle()
	local pagename = self.title.text

	-- Exit if we have been told not to set a title or if the title begins with
	-- an opening parenthesis.
	if self.noDisplayTitle or pagename:find('^%(') then
		return nil
	end

	-- Find the display base and the display parentheses.
	local dBase = self.displayTitleBase
	local dParen = self.displayTitleParen
	if not dBase or not dParen then
		
		local base, paren = pagename:match('^(.*)%s*%((.-)%)$')
		if not base then
			base = pagename
		end
		-- Use the values we found, but only if a value has not already been
		-- specified.
		dBase = dBase or base
		dParen = dParen or paren
	end

	-- Build the display string
	local display
	if dParen then
		display = string.format('%s <small>(%s)</small>', dBase, dParen)
	else
		display = dBase
	end
	if self.title.namespace ~= 0 then
		display = mw.site.namespaces[self.title.namespace].name .. ':' .. display
	end

	-- Return the expanded DISPLAYTITLE parser function.
	return mw.getCurrentFrame():preprocess(string.format(
		'{{DISPLAYTITLE:%s}}',
		display
	))
end

-- Renders an eras icon from the given icon data. It deals with the image,
-- tooltip, link, and the category, but not the protection fields.
function Eras:renderIcon(data)
	-- Render the category at the end if it exists.
	if data.category then
		self:addCategory(data.category)
	end
	-- Render the icon and return it.
	local ret = {}
	ret[#ret + 1] = '[[File:'
	ret[#ret + 1] = data.image
	if data.tooltip then
		ret[#ret + 1] = '|'
		ret[#ret + 1] = data.tooltip
	end
	if data.link then
		ret[#ret + 1] = '|link='
		ret[#ret + 1] = data.link
	end
	ret[#ret + 1] = ']]'
	return table.concat(ret)
end

-- Renders the icons that respond to a publishing era.
function Eras:renderPublishingIcons()
	local ret = {}
	local codes = {'btr', 'old', 'gpr', 'tcw', 'imp', 'reb', 'new', 'njo', 'leg'}
	local has_icon = false
	for _, code in ipairs(codes) do
		local data = self:getIconData(code)
		if data then
			ret[#ret + 1] = self:renderIcon(data)
			has_icon = true
		end
	end
	
	if not has_icon then
		self:addCategory('Articles with no specified publishing era')
	end
	
	return table.concat(ret)
end

-- Render all the icons and eclose them in a surrounding div tag.
function Eras:renderIcons()
	local icons = {}
	icons[#icons + 1] = self:renderPublishingIcons()
	icons = table.concat(icons)

	local root = mw.html.create('div')
	root
		:attr('id', 'title-eraicons')
		:css('float', 'right')
		:css('position', 'static')
		:wikitext(icons)

	return tostring(root)
end

-- Render all the categories that were specified using Eras:addCategory or with
-- category flags.
function Eras:renderCategories()
	local fullPagename = self.title.prefixedText
	if fullPagename == 'Template:Top' then
		-- Exit if we are on a blacklisted page.
		return nil
	end

	local pagename = self.title.text

	-- Renders one category.
	local function renderCategory(cat, sort)
		return string.format(
			'[[%s:%s|%s]]', 'Category', cat, sort or pagename
		)
	end

	local ret = {}

	-- Render categories from Eras:addCategory
	for i, t in ipairs(self.categories) do
		ret[i] = renderCategory(t.category, t.sortKey)
	end

	-- Render categories from category flags.
	if self.hasBadParameter then
		ret[#ret + 1] = renderCategory(
			'Pages with bad parameters in Template:Top'
		)
	end

	return table.concat(ret)
end

-- Add __NOTOC__ if needed
function Eras:renderNotoc()
	if self.hideToc then
		return '__NOTOC__'
	end
	return nil
end

-- This method is called when the tostring function is used on the Eras object.
-- (This works in a similar fashion to Eras.__index above.) It calls all the
-- top-level render methods and returns the final output.
function Eras:__tostring()
	local ret = {}
	ret[#ret + 1] = self:renderDisplayTitle()
	ret[#ret + 1] = self:renderIcons()
	ret[#ret + 1] = self:renderCategories()
	ret[#ret + 1] = self:renderNotoc()
	return table.concat(ret)
end

-------------------------------------------------------------------------------
-- Exports
-------------------------------------------------------------------------------

local p = {}

-- This function is the entry point from other Lua modules.
function p._main(args)
	-- Define a function to call from pcall so that we can catch any errors
	-- and display them to the user rather than the cryptic "Script error".
	-- (It's not so cryptic if you click on it to see the error message, but
	-- not so many users know to do that.)
	local function getErasResult ()
		local erasObj = Eras.new(args)
		-- Temporary hack to hide ugly error message on LEGO articles
		if erasObj == false then
			return '[[' .. 'Category:Pages with bad parameters in Template:Top]]'
		end
		return tostring(erasObj)
	end

	-- Get the result. We only catch errors if debug mode is set to false.
	local success, result
	if DEBUG_MODE then
		success = true
		result = getErasResult()
	else
		success, result = pcall(getErasResult)
	end

	-- Return the result if there were no errors, and a formatted error message 
	-- if there were.
	if success then
		return result
	else
		return string.format(
			'<strong class="error">[[Template:Eras]] error: %s.</strong>' ..
			'[[' .. 'Category:Pages with bad parameters in Template:Top]]',
			result -- this is the error message
		)
	end
end

-- This is the function accessed from wikitext. It must be accessed through
-- a template. The template should transclude only the text
-- "{{#invoke:Eras|main}}", and then when that template is used, any arguments
-- passed to it are magically sent through to the module.
function p.main(frame)
	local args = {}
	for k, v in pairs(frame:getParent().args) do
		v = v:match('^%s*(.-)%s*$') -- trim whitespace
		if v ~= '' then
			args[k] = v
		end
	end
	return p._main(args)
end

return p

-- </nowiki>
-- [[Category:Eras utility templates|{{PAGENAME}}]]
