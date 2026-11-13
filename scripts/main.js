// Core Link is a remote terminal for the team's existing core inventory.
// It does not create a second stockpile or add any item capacity.

function syncCoreLink(build){
    var core = build.team == null ? null : build.team.core();

    // StorageBuild uses linkedCore to forward normal storage behavior to a core.
    // Keep the item module reference in sync as cores can be added or destroyed.
    build.linkedCore = core;
    if(core != null){
        build.items = core.items;
    }else{
        // With no active core, do not keep a stale reference to a destroyed
        // core's inventory. The terminal has no independent stockpile.
        build.items = new ItemModule();
    }
    return core;
}

function detachCoreLink(build){
    // Never let the removed building retain the shared core ItemModule.
    build.linkedCore = null;
    build.items = new Packages.mindustry.world.modules.ItemModule();
}

const coreLink = Vars.content.block("mass-driver-tiers-core-link");
if(coreLink == null){
    throw new Error("Core Link block definition was not loaded before scripts/main.js.");
}

coreLink.buildType = prov(() => new JavaAdapter(StorageBlock.StorageBuild, {
    updateTile(){
        syncCoreLink(this);
    },

    onProximityUpdate(){
        this.super$onProximityUpdate();
        syncCoreLink(this);
    },

    acceptItem(source, item){
        var core = syncCoreLink(this);
        return core != null && this.super$acceptItem(source, item);
    },

    handleItem(source, item){
        if(syncCoreLink(this) != null){
            this.super$handleItem(source, item);
        }
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

    write(write){
        // Avoid serializing a duplicate copy of the team's entire inventory
        // for every Core Link. The actual core remains the stockpile owner.
        var previousItems = this.items;
        syncCoreLink(this);
        this.items = new Packages.mindustry.world.modules.ItemModule();
        try{
            this.super$write(write);
        }finally{
            this.items = previousItems;
            syncCoreLink(this);
        }
    },

    removeStack(item, amount){
        if(syncCoreLink(this) == null) return 0;
        // StorageBuild updates campaign core-item counts for linked storage.
        return this.super$removeStack(item, amount);
    },

    itemTaken(item){
        if(syncCoreLink(this) != null){
            this.super$itemTaken(item);
        }
    },

    getMaximumAccepted(item){
        return syncCoreLink(this) == null ? 0 : this.super$getMaximumAccepted(item);
    },

    canUnload(){
        return syncCoreLink(this) != null && this.super$canUnload();
    },

    // Never spill the shared team inventory when this building is destroyed.
    explosionItemCap(){
        return 0;
    },

    onDeconstructed(){
        detachCoreLink(this);
        this.super$onDeconstructed();
    },

    onRemoved(){
        detachCoreLink(this);
        this.super$onRemoved();
    }
}, coreLink));
