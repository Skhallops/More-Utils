// Core Link is a remote interface to the team's existing core inventory.
// StorageBlock.StorageBuild already forwards normal item handling to linkedCore.
// This script only maintains the remote link and protects the shared inventory
// from being serialized once for every Core Link.

function syncCoreLink(build){
    var core = build.team == null ? null : build.team.core();

    build.linkedCore = core;
    // StorageBuild.removeStack() operates on this items module, so it must be
    // the same module used by the core. A missing core gets a private empty
    // module; itemCapacity is zero so that module cannot accept items.
    build.items = core == null ? new ItemModule() : core.items;
    return core;
}

const coreLink = Vars.content.block("mass-driver-tiers-core-link");
if(coreLink == null){
    throw new Error("Core Link block definition was not loaded before scripts/main.js.");
}

// These are set here as well as in JSON to make the runtime requirements
// explicit. Shared core items are synchronized by the core, not by this block.
coreLink.update = true;
coreLink.sync = false;
coreLink.hasItems = true;
coreLink.acceptsItems = true;
coreLink.unloadable = true;
coreLink.itemCapacity = 0;
coreLink.coreMerge = false;

coreLink.buildType = prov(() => extend(StorageBlock.StorageBuild, coreLink, {
    updateTile(){
        syncCoreLink(this);
    },

    onProximityUpdate(){
        this.super$onProximityUpdate();
        syncCoreLink(this);
    },

    write(write){
        // Do not write the shared core inventory into every remote terminal.
        // The CoreBuild is the single authoritative owner of that inventory.
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
}));

print("Core Link runtime initialized for " + coreLink.name);
