-- The pinned luaotfload loader keys OTF data by basename, size and mtime.
-- Equal font copies at distinct pinned paths can therefore exchange source
-- identities. Namespace its native cache by the full resolved path, retaining
-- the loader's subfont, feature, timestamp and version checks inside each cache.
local otf = assert(fonts.handlers.otf)
if otf.jlpt_path_cache_v1 then return end
local containers = assert(luaotfload.fontloader.containers)
local native_load = assert(otf.load)
local digest = assert(md5.sumhexa)
otf.load = function(filename, sub, instance)
  local identity = filename:gsub("\\", "/")
  if not identity:match("^%a:/") and identity:sub(1, 1) ~= "/" then
    identity = lfs.currentdir():gsub("\\", "/") .. "/" .. identity
  end
  local previous = otf.cache
  otf.cache = containers.define("fonts", "jlpt-otl-path-v1-" .. digest(identity), otf.version, true)
  local ok, result = xpcall(function()
    return native_load(filename, sub, instance)
  end, debug.traceback)
  otf.cache = previous
  if not ok then error(result, 0) end
  return result
end
otf.jlpt_path_cache_v1 = true
