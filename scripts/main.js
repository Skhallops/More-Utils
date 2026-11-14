// Core Link is a remote terminal for the team's real core inventory.
//
// Mindustry v8 load order is important: scripts/main.js runs BEFORE JSON mod
// content is parsed. Mods.loadContent() then fires ModContentLoadEvent after
// every JSON file has been loaded but BEFORE Block.init() creates build types.
// Register the custom build provider in that event, not at script top level.
//
// The runtime build deliberately extends plain Building, not
// StorageBlock.StorageBuild. DirectionalUnloader rejects linked StorageBuild
// instances by default (allowCoreUnload is false), but accepts an ordinary
// Building that exposes the same live core ItemModule and canUnload behavior.
// The block definition stays a StorageBlock so Core Link does not output
// directly onto conveyors; use an Unloader for item withdrawal.

function coreForLink(build){
    if(build == null || build.team == null) return null;
    return build.team.core();
}

function syncCoreLink(build){
    var core = coreForLink(build);

    if(core == null){
        // Do not retain the old core's inventory after the team's core is gone.
        if(build._coreLinkBoundCore != null || build.items == null){
            build.items = new ItemModule();
        }
        build._coreLinkBoundCore = null;
        return null;
    }

    // Expose the real ItemModule so vanilla DirectionalUnloader can see it.
    // Rebind if the team switches cores or the core's ItemModule is replaced.
    if(build.items !== core.items){
        build.items = core.items;
    }
    build._coreLinkBoundCore = core;
    return core;
}

function detachCoreLink(build){
    // Never leave a removed terminal pointing at the team's inventory.
    build.items = new ItemModule();
    build._coreLinkBoundCore = null;
}

// Arc-reactor ambience for the Core Link. These are built once after content
// loads so the terminal visibly "breathes" and sparks when stock moves.
var coreLinkPulseFx = null;
var coreLinkSparkFx = null;

function makeCoreLinkFx(){
    if(coreLinkPulseFx != null) return;

    coreLinkPulseFx = new WaveEffect();
    coreLinkPulseFx.colorFrom = Color.valueOf("cffae8");
    coreLinkPulseFx.colorTo = Color.valueOf("3faaa4");
    coreLinkPulseFx.sizeFrom = 5;
    coreLinkPulseFx.sizeTo = 34;
    coreLinkPulseFx.strokeFrom = 2.5;
    coreLinkPulseFx.strokeTo = 0;
    coreLinkPulseFx.lifetime = 34;
    coreLinkPulseFx.lightColor = Color.valueOf("85e0c6");
    coreLinkPulseFx.lightOpacity = 0.3;
    coreLinkPulseFx.init();

    coreLinkSparkFx = new ParticleEffect();
    coreLinkSparkFx.line = true;
    coreLinkSparkFx.particles = 4;
    coreLinkSparkFx.length = 10;
    coreLinkSparkFx.cone = 360;
    coreLinkSparkFx.colorFrom = Color.valueOf("cffae8");
    coreLinkSparkFx.colorTo = Color.valueOf("3faaa4");
    coreLinkSparkFx.strokeFrom = 2;
    coreLinkSparkFx.strokeTo = 0.2;
    coreLinkSparkFx.lenFrom = 4;
    coreLinkSparkFx.lenTo = 1;
    coreLinkSparkFx.lifetime = 16;
    coreLinkSparkFx.init();
}

function tickCoreLinkFx(build){
    build._coreLinkPulseTicks = (build._coreLinkPulseTicks || 0) + 1;
    build._coreLinkSparkWait = Math.max(0, (build._coreLinkSparkWait || 0) - 1);

    if(build._coreLinkDirty && build._coreLinkSparkWait <= 0){
        build._coreLinkDirty = false;
        build._coreLinkSparkWait = 12;
        if(!Vars.headless) coreLinkSparkFx.at(build.x, build.y);
    }

    if(build._coreLinkPulseTicks >= 210){
        build._coreLinkPulseTicks = 0;
        if(!Vars.headless) coreLinkPulseFx.at(build.x, build.y);
    }
}

function installCoreLink(){
    var coreLink = Vars.content.block("more-utils-core-link");
    if(coreLink == null){
        throw new Error("Core Link block was not found after mod JSON content loading.");
    }

    // The core owns and synchronizes the only inventory. This terminal has no
    // local capacity and must not sync or save a second copy of core items.
    coreLink.update = true;
    coreLink.sync = false;
    coreLink.hasItems = true;
    coreLink.acceptsItems = true;
    coreLink.unloadable = true;
    coreLink.itemCapacity = 0;
    coreLink.coreMerge = false;
    coreLink.alwaysAllowDeposit = true;

    makeCoreLinkFx();

    coreLink.buildType = prov(function(){
        return new JavaAdapter(Building, {
            // Do NOT bind items in created() or onProximityUpdate(). During
            // save loading, Tile.setBlock() creates the entity before
            // readAll() reads its saved (empty) module. updateTile() binds only
            // after the map has finished loading, preventing that empty module
            // from overwriting the real core inventory.

            updateTile(){
                syncCoreLink(this);
                tickCoreLinkFx(this);
            },

            acceptItem(source, item){
                var core = syncCoreLink(this);
                return core != null && core.acceptItem(source, item);
            },

            handleItem(source, item){
                var core = syncCoreLink(this);
                if(core != null){
                    // Keep CoreBuild's own campaign/statistics behavior.
                    core.noEffect = true;
                    core.handleItem(source, item);
                    this._coreLinkDirty = true;
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
                    this._coreLinkDirty = true;
                }
            },

            removeStack(item, amount){
                var core = syncCoreLink(this);
                if(core == null) return 0;
                var taken = core.removeStack(item, amount);
                if(taken > 0) this._coreLinkDirty = true;
                return taken;
            },

            itemTaken(item){
                var core = syncCoreLink(this);
                if(core != null){
                    // Unloader removes directly from this.items, then calls
                    // itemTaken(). Forward campaign accounting to CoreBuild.
                    core.itemTaken(item);
                    this._coreLinkDirty = true;
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

            allowDeposit(){
                return true;
            },

            canPickup(){
                // A proxy to the team's inventory must never become a payload.
                return false;
            },

            explosionItemCap(){
                // The team's inventory must never contribute to this terminal's
                // destruction drops or explosion.
                return 0;
            },

            write(write){
                // Store an empty local module. The core serializes its inventory
                // once through its own entity save data.
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
        });
    });

    print("[More Utils] Core Link runtime registered after JSON content loading.");
}

// scripts/main.js runs before the mod's JSON content exists. This event is
// explicitly fired after Mods.loadContent() parses JSON and before content.init().
Events.on(ModContentLoadEvent, cons(function(event){
    try{
        installCoreLink();
    }catch(error){
        print("[More Utils] Core Link registration FAILED: " + error);
    }
}));

print("[More Utils] Core Link waiting for ModContentLoadEvent.");
