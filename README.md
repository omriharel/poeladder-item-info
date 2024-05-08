# poeladder-item-info

A community-maintained repository of SSF-oriented Unique acquisition methods. _See example here_ (← this will be a link)

## Overview

This project aims to provide Path of Exile players with community-sourced data about the different available acquisition methods for many Unique items - specifically in the context of an SSF (Solo Self-Found) environment.

The data from this project is viewable inside [poeladder.com](https://poeladder.com), the Unique collection one-stop-shop for SSF players - built by [@halfacandan](https://github.com/halfacandan). Simply click an item anywhere on the site and you'll be redirected to its dedicated item page. You'll find acquisition data from this project under the **Community Notes** section:

> (screenshot can go here)

## How can I help?

Contributing new data for a Unique is easy! All you need is a GitHub account. **No coding experience is necessary.**

You can do everything right from your browser, but you can greatly enhance your experience if you use an IDE (such as [VSCode](https://code.visualstudio.com/download), which we recommend for this project). Read more on this [below](#recommended-ide).

There are three primary ways you can contribute to this project:

- Adding data for items that don't have any yet ← add heading links
- Updating data for items with outdated data    ←
- Reporting outdated data                       ←

All of these are helpful and we appreciate you for taking the time! Read on below for more info and a quick how-to.

## How does this work?

This project heavily leverages automation to help us ensure the data used by PoE Ladder remains consistent in its structure, and that changes to it are easy to review and tweak as necessary. It utilizes the standard GitHub PR workflow for collaboration, and GitHub Actions for data validation and the construction of the compiled data thats ends up on the website.

Here's a brief overview of how it's built, for the more tech-savvy folks:

- Items are organized into a class-based file hierarchy, with each item having its own YAML file, e.g. **`items/belts/Mageblood.yml`**
  - YAML files are easy to read and edit, which makes it possible for anyone to contribute changes
  - The file hierarchy mirrors that of the Unique collection tab, and as such it's easily browseable
- Each YAML file details one or more **acquisition methods** for its corresponding item
  - There are different types of acquisition methods for items - some can be farmed with a div card, others drop from a boss, others have a vendor recipe associated with them, etc.
  - Items with different variants (such as Precursor's Emblem rings) list each variant individually
- When a PR is opened, [a GitHub Actions workflow](./.github/workflows/ci.yml) is run. This workflow validates each individual item file against an **[item schema](./schemas/single-item.schema.json)**, which ensures the data for this item is kept in the predictable structure expected by PoE Ladder
  - If a file doesn't pass validation, a comment is automatically posted on the PR and lets the author know that there are validation errors that need to be fixed
  - This schema also provides **automatic code completion** when using VSCode with the [YAML Language Support by Red Hat](https://marketplace.visualstudio.com/items?itemName=redhat.vscode-yaml) extension installed (this is the reason an IDE is encouraged)
- When a PR is merged to the `master` branch, all data is compiled (by [a different GitHub Actions workflow](./.github/workflows/release.yml)) into a single JSON file, which is then automatically made into a GitHub release for this repository. The [latest release](https://github.com/omriharel/poeladder-item-info/releases/tag/latest) always contains the most up-to-date version of this data, which can be downloaded directly [here](https://github.com/omriharel/poeladder-item-info/releases/download/latest/item-data.json)


## Contribution prerequisites

The only requirement is a **GitHub account**. You can [create one for free](https://github.com/join) if you don't have one.

### Recommended: IDE

While it is possible to make and submit changes using only your browser, we recommend to use an IDE (short for _Integrated Development Environment_).

We specifically recommend [VSCode](https://code.visualstudio.com/download) with the [YAML Language Support by Red Hat](https://marketplace.visualstudio.com/items?itemName=redhat.vscode-yaml) extension, which you can install directly inside VSCode by opening the Extensions pane (or from the link here).

The reason we're recommending this specific extension is a powerful feature it enables - **code completion**:

![Code completion in action](./docs/assets/code_completion.png)

> Code completion works in real-time to help you fill out different details according to the item schema - it makes it very easy to add data and ensure that it validates correctly before you submit your changes for review.

## How do I add or edit data?

> The following explanation does not include specific instructions for how to do each of the steps on GitHub, it only serves as an overview. If you need any assistance with this, please [reach out to us](https://discord.gg/WXPJ6He2HA)! We'd be happy to help.

The general contribution workflow is a collaborative effort between a person wanting to contribute a set of changes (**"Author"**) and people who maintain the project's main repository (**"Maintainers"**).

At a baseline, it works like this:

- Author **forks the repository**, creating their own copy of it
- Author **creates a new branch** under their fork of the repository. This branch represents the _entire_ set of changes they would like to contribute (e.g. be adding data for one or more items)
- Author **works on their changes in their branch, committing and pushing them freely** as they progress
- When Author is ready to contribute their changes back to the main repository, they **open a Pull Request (PR)** for their branch
- An **automated check* will run at that point. It takes between 30 seconds to a minute to complete. After it runs, if there are any validation errors in any of the files added or changed by Author, an automatic comment will be posted onto the Pull Request detailing the errors and requesting Author to make fixes and adjustments to them
- Author can fix any errors and push to their branch again. A separate check will occur for every push, until there are no errors
- Once the PR passes the validation, it is **ready for review**. At this point one or more Maintainers can review the changes by hand, ensuring that the contributed data is accurate and verified at the time of submission
- After the PR passes review, it is **ready to merge**. A maintainer can then merge it to the `master` branch of the main repository, at which point it will automatically be included in a release and ready for integration into PoE Ladder.

If this seems overwhelming, have no fear - this workflow is more simple than it sounds, and we're more than happy to guide you through it. Please [reach out to us in the _#community-item-info_ channel of the PoE Ladder Discord server](https://discord.gg/WXPJ6He2HA).
