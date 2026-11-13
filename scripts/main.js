// Core Link is a remote interface to the team's existing core inventory.
// StorageBlock.StorageBuild already forwards item handling to linkedCore.
// This script attaches that native behavior to the JSON-defined Core Link.

function syncCoreLink(build){
    var core = build.team == null ? null : build.team.core();

    build.linkedCore = core;
    // Mirror the core module because StorageBuild.removeStack() acts on
    // this.items. Without a core, keep an empty private module.
    build.items = core == null ? new ItemModule() : core.items;
    return core;
}

const coreLink = Vars.content.block("mass-driver-tiers-core-link");
if(coreLink == null){
    throw new Error("Core Link block definition was not loaded before scripts/main.js.");
}

// The core owns and synchronizes the shared inventory. This terminal must not
// create additional capacity or send duplicate copies of the inventory.
coreLink.update = true;
coreLink.sync = false;
coreLink.hasItems = true;
coreLink.acceptsItems = true;
coreLink.unloadable = true;
coreLink.itemCapacity = 0;
coreLink.coreMerge = false;

// IMPORTANT: use JavaAdapter to create a StorageBuild instance for this
// existing block. extend() creates a Block subclass and is not a Building
// constructor, so it must not be used here.
coreLink.buildType = prov(() => new JavaAdapter(StorageBlock.StorageBuild, {
    updateTile(){
        // Keep remote terminals attached if the team's core changes.
        syncCoreLink(this);
    },

    onProximityUpdate(){
        this.super$onProximityUpdate();
        syncCoreLink(this);
    },

    write(write){
        // The core is the authoritative owner of this shared ItemModule.
        // Write an empty module for this remote terminal, then restore the
        // shared module in a finally block even if serialization fails.
        var sharedItems = this.items;
        this.items = new ItemModule();
        try{
            this.super$write(write);
        }finally{
            this.items = sharedItems;
        }
    },

    explosionItemCap(){
        // Destroying a remote terminal must never spill the team's inventory.
        return 0;
    }
}, coreLink));

print("[More Utils] Core Link StorageBuild adapter registered.");
