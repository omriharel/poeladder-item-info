# poeladder-item-info

A community-maintained repository of SSF-oriented Unique acquisition methods. _See example here_ (← this will be a link)

## Overview

This project aims to provide Path of Exile players with community-sourced data about the different available acquisition methods for many Unique items - specifically in the context of an SSF (Solo Self-Found) environment.

The data from this project is viewable inside [poeladder.com](https://poeladder.com), the Unique collection one-stop-shop for SSF players - built by the talented [@halfacandan](https://github.com/halfacandan). Simply click an item anywhere on the site and you'll be redirected to its dedicated item page. You'll find acquisition data from this project under the **Community Notes** section:

> (screenshot can go here)

## How can I help?

Contributing new data for a Unique is easy! All you need is a GitHub account. You can do everything right from your browser, but you can greatly enhance your experience if you use an IDE to add/edit files on your machine instead.

There are three primary ways you can contribute to this project:

- Adding data for items that don't have any yet ← add heading links
- Updating data for items with outdated data    ←
- Reporting outdated data                       ←

All of these are helpful and we appreciate you for taking the time! Read on below for more info and a quick how-to.

## How does this work?

This project heavily leverages automation to help us ensure the data used by PoE Ladder remains consistent in its structure, and that changes to it are easy to review and tweak as necessary. It utilizes the standard GitHub PR workflow for collaboration, and GitHub Actions for data validation and the construction of the compiled data thats ends up on the website.

Here's a brief overview of how it's built, for the more tech-savvy folks:

- Items are organized into a class-based file hierarchy, with each item having its own YAML file, e.g. **`items/belts/Mageblood.yml`**
  - YAML files are easy to read and edit, which makes it possible for less technical people to contribute changes
  - The file hierarchy mirrors that of the Unique collection tab, and as such it's easily browseable
- Each YAML file details one or more **acquisition methods** for its corresponding item
  - There are different types of acquisition methods for items - some can be farmed with a div card, others drop from a boss, others have a vendor recipe associated with them, etc.
  - Items with different variants (such as Precursor's Emblem rings) list each variant individually
- When a PR is opened, a GitHub Actions workflow is run. This workflow validates each individual item file against an **item schema**, which ensures the data for this item is kept in the predictable structure expected by PoE Ladder
  - If a file doesn't pass validation, a comment is automatically posted on the PR and lets the author know that there are validation errors that need to be fixed
- When a PR is merged to the `master` branch, all data is compiled (by a different GitHub Actions workflow) into a single JSON file, which is then automatically made into a GitHub release for this repository. The [latest release](https://github.com/omriharel/poeladder-item-info/releases/tag/latest) always contains the most up-to-date version of this data, which can be downloaded directly [here](https://github.com/omriharel/poeladder-item-info/releases/download/latest/item-data.json).
