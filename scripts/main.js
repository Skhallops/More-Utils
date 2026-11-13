// Core Link is a remote terminal for the team's real core inventory.
//
// IMPORTANT: this build intentionally extends plain Building, NOT
// StorageBlock.StorageBuild. Mindustry's DirectionalUnloader rejects targets
// that are StorageBuild instances with linkedCore set unless the unloader has
// allowCoreUnload enabled. A plain Building proxy avoids that vanilla class
// check while still presenting the core's live ItemModule to the unloader.
//
// StorageBlock remains the block definition so it keeps the vanilla storage
// block's no-direct-conveyor-output behavior and visual/category defaults.

function coreForLink(build){
    if(build == null || build.team == null) return null;
    return build.team.core();
}

function syncCoreLink(build){
    var core = coreForLink(build);
    build.items = core == null ? new ItemModule() : core.items;
    return core;
}

function detachCoreLink(build){
    // Never leave a removed terminal pointing at the team's inventory.
    build.items = new ItemModule();
}

const coreLink = Vars.content.block("mass-driver-tiers-core-link");
if(coreLink == null){
    throw new Error("[More Utils] Core Link JSON block was not loaded.");
}

// The core owns the only inventory. The terminal has no private capacity and
// must not independently sync or save a second copy of the core's items.
coreLink.update = true;
coreLink.sync = false;
coreLink.hasItems = true;
coreLink.acceptsItems = true;
coreLink.unloadable = true;
coreLink.itemCapacity = 0;
coreLink.coreMerge = false;
coreLink.alwaysAllowDeposit = true;

// Do not use StorageBlock.StorageBuild here: vanilla DirectionalUnloader has
// a hard class check that rejects linked StorageBuild targets by default.
coreLink.buildType = prov(() => new JavaAdapter(Building, {
    created(){
        this.super$created();
        syncCoreLink(this);
    },

    onProximityUpdate(){
        this.super$onProximityUpdate();
        syncCoreLink(this);
    },

    updateTile(){
        // Rebind if a core is added, destroyed, or replaced.
        syncCoreLink(this);
    },

    acceptItem(source, item){
        var core = syncCoreLink(this);
        return core != null && core.acceptItem(source, item);
    },

    handleItem(source, item){
        var core = syncCoreLink(this);
        if(core != null){
            // Use CoreBuild's own path so campaign statistics and item counts
            // are updated exactly as if the conveyor fed the core directly.
            core.handleItem(source, item);
        }
    },

    getMaximumAccepted(item){
        var core = syncCoreLink(this);
        return core == null ? 0 : core.getMaximumAccepted(item);
    },

    acceptStack(item, amount, source){
        var core = syncCoreLink(this);
        return core == null ? 0 : core.acceptStack(item, amount, source);
    },

    handleStack(item, amount, source){
        var core = syncCoreLink(this);
        if(core != null){
            core.handleStack(item, amount, source);
        }
    },

    removeStack(item, amount){
        var core = syncCoreLink(this);
        return core == null ? 0 : core.removeStack(item, amount);
    },

    itemTaken(item){
        var core = syncCoreLink(this);
        if(core != null){
            // DirectionalUnloader removes directly from this.items, then calls
            // itemTaken(). Forward that callback for campaign item accounting.
            core.itemTaken(item);
        }
    },

    canUnload(){
        var core = syncCoreLink(this);
        return core != null && core.canUnload();
    },

    sense(sensor){
        var core = syncCoreLink(this);
        if(sensor == LAccess.itemCapacity){
            return core == null ? 0 : core.sense(sensor);
        }
        return this.super$sense(sensor);
    },

    canPickup(){
        // A proxy to the team inventory must never become a payload.
        return false;
    },

    explosionItemCap(){
        // The team's inventory is not stored in this building and must never
        // contribute to this terminal's destruction drops/explosion.
        return 0;
    },

    write(write){
        // Save an empty module for the terminal. The core is the sole owner of
        // the inventory and will serialize it once in its own save data.
        var sharedItems = this.items;
        this.items = new ItemModule();
        try{
            this.super$write(write);
        }finally{
            this.items = sharedItems;
        }
    },

    onDeconstructed(builder){
        detachCoreLink(this);
        this.super$onDeconstructed(builder);
    },

    onDestroyed(){
        detachCoreLink(this);
        this.super$onDestroyed();
    },

    onRemoved(){
        detachCoreLink(this);
        this.super$onRemoved();
    }
}));

print("[More Utils] Core Link plain-Building proxy registered; linked inventory will use core storage.");
