# Consumable data reuse

This directory is meant to contain .yml files to keep reusable consumable data. This uses the same schema as consumable, and is represented as a mapping between internal IDs and the consumable data for that ID. For example, if this directory will contain the following `.yml` file:

```yaml
blightedMap:
  type: map
  name: Blighted map
  text: Available in blight reward chests from Fungal Growth encounters in maps. Maps with narrow layouts - such as Phantasmagoria - offer more blight reward chests
  wiki: https://www.poewiki.net/wiki/Blighted_map
```

You will be able to reference it in an item data file like so:

```yaml
acquisitionMethods:
  - type: leagueContent
    leagueName: Blight
    text: This unique has a chance to drop at the centre of the Purification Pump once all enemies in the map have been defeated
    frequency: extremely-rare
    consumable:
      id: blightedMap
```

As you see, instead of inlining the same consumable data multiple times across different files, you can now simply refer to the `blightedMap` internal ID (given by the property name in the first YAML) to have this data seamlessly copied there.

## Implementation details

- This mapping of internal IDs to consumable data may span multiple files, but duplicate keys across files result in undefined behavior. Please make sure to use separate IDs through naming conventions or namespacing.
- Internal IDs are case-sensitive.

## Caution! ⚠

This data is validated for the consumable schema ONLY when using the YAML Language Support extension in VSCode (with the configuration provided in `.vscode/settings.json` in this repository).

The build script which composes the main JSON output file for this project will validate item data files _either_ for a reference ID being present, or the same consumable structure as exists before this change - either may be used, but when a reference ID is used - no further validation of its structure takes place during runtime. **This means you can easily break things by not using the VSCode extension to validate your work on files in the `consumables` directory. It is highly advisable to avoid changing these files without the extension.**

You will still receive a proper error when using an invalid reference ID (if it's missing, for example). But you're not protected from broken structure when using reference IDs. You have been warned.
