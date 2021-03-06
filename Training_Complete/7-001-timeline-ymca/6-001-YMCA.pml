<?xml version="1.0" encoding="UTF-8" ?>
<Package name="6-001-YMCA" format_version="4">
    <Manifest src="manifest.xml" />
    <BehaviorDescriptions>
        <BehaviorDescription name="behavior" src="behavior_1" xar="behavior.xar" />
        <BehaviorDescription name="behavior" src="WaitStopTimeline" xar="behavior.xar" />
        <BehaviorDescription name="behavior" src="Y" xar="behavior.xar" />
    </BehaviorDescriptions>
    <Dialogs />
    <Resources>
        <File name="elephant" src="Y/elephant.ogg" />
        <File name="MyPkanarMove" src="MyPkanarMove.pmt" />
        <File name="t" src="t.pmt" />
    </Resources>
    <Topics />
    <IgnoredPaths>
        <Path src=".metadata" />
    </IgnoredPaths>
    <Translations auto-fill="en_US">
        <Translation name="translation_en_US" src="translations/translation_en_US.ts" language="en_US" />
    </Translations>
</Package>
