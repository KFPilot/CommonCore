//Common Core CoreWeapon
//Distributed under the terms of the MIT License.
//For more information see https://github.com/KFPilot/CommonCore.
class CoreWeapon extends Engine.Weapon
	abstract;

var CorePlayerReplicationInfo InstigatorPlayerReplicationInfo;

//If specified, the OriginalWeaponClass' localized strings will be used instead of the ones specified on this weapon.
var const class<Weapon> OriginalWeaponClass;

var array<SparseWeaponReplicationInfo> SparseReplicationInfoList;
delegate OnReceiveSparseReplicationInfo(CoreWeapon Weapon, SparseWeaponReplicationInfo ReplicationInfo);

//Helper functions.
final static function string GetWeaponName()
{
	if (default.OriginalWeaponClass != None)
	{
		return default.OriginalWeaponClass.default.ItemName;
	}

	return default.ItemName;
}

final static function string GetWeaponDescription()
{
	if (default.OriginalWeaponClass != None)
	{
		return default.OriginalWeaponClass.default.Description;
	}

	return default.Description;
}

final simulated function CorePlayerReplicationInfo GetPlayerReplicationInfo()
{
	if (InstigatorPlayerReplicationInfo == None)
	{
		InstigatorPlayerReplicationInfo = CorePlayerReplicationInfo(Instigator.PlayerReplicationInfo);
	}

	return InstigatorPlayerReplicationInfo;
}

//SparseWeaponReplicationInfo functions.
simulated function SparseWeaponReplicationInfo GetSparseInfo(class<SparseWeaponReplicationInfo> SparseWeaponClass)
{
	local int Index;
    for (Index = SparseReplicationInfoList.Length - 1; Index >= 0; Index--)
	{
		if (ClassIsChildOf(SparseReplicationInfoList[Index].Class, SparseWeaponClass))
		{
			return SparseReplicationInfoList[Index];
		}
	}

	return None;
}

simulated function RegisterSparseInfo(SparseWeaponReplicationInfo SPRI)
{
    SparseReplicationInfoList[SparseReplicationInfoList.Length] = SPRI;
	OnReceiveSparseReplicationInfo(Self, SPRI);
}

simulated function UnregisterSparseInfo(SparseWeaponReplicationInfo SPRI)
{
    local int Index;
    for (Index = SparseReplicationInfoList.Length - 1; Index >= 0; Index--)
    {
        if (SparseReplicationInfoList[Index] == SPRI)
        {
            SparseReplicationInfoList.Remove(Index, 1);
            return;
        }
    }
}

defaultproperties
{

}