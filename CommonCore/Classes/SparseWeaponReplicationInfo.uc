//Common Core SparseWeaponReplicationInfo
//Distributed under the terms of the MIT License.
//For more information see https://github.com/KFPilot/CommonCore.
class SparseWeaponReplicationInfo extends SparseReplicationInfo;

var CoreWeapon OwningWeapon;

static function SparseReplicationInfo Find(Actor InSparseOwningActor)
{
    local CoreWeapon Weapon;

    if (InSparseOwningActor == None)
    {
        return None;
    }

    Weapon = CoreWeapon(InSparseOwningActor);
    if (Weapon == None)
    {
        Warn("Find: " $ default.Class $ " was subclassed from SparseWeaponReplicationInfo but InSparseOwningActor is not a CoreWeapon (was a " $ InSparseOwningActor $ ").");
        return None;
    }

    return Weapon.GetSparseInfo(default.Class);
}

protected simulated function bool AttemptRegister()
{
    if (SparseOwningActor == None)
    {
        return false;
    }

    OwningWeapon = CoreWeapon(SparseOwningActor);
    if (OwningWeapon == None)
    {
        Warn("AttemptRegister: " $ Class $" was subclassed from SparsePlayerReplicationInfo but SparseOwningActor is not a CoreWeapon (was a " $ SparseOwningActor $ ").");
        return false;
    }

    OwningWeapon.RegisterSparseInfo(Self);
    return true;
}

protected simulated function Unregister()
{
    if (OwningWeapon == None)
    {
        return;
    }

    OwningWeapon.UnregisterSparseInfo(Self);
}

defaultproperties
{
	RemoteRole=ROLE_SimulatedProxy
    NetUpdateFrequency=0.1
    bAlwaysRelevant=true
    bOnlyRelevantToOwner=true
}