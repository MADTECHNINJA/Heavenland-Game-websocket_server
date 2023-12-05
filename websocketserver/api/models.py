from django.db import models


class Building(models.Model):
    username = models.CharField(max_length=32, db_index=True)
    name = models.CharField(max_length=64, null=True, blank=True)
    thumbnail_url = models.CharField(max_length=128, null=True, blank=True)


class BuildingBlock(models.Model):
    building_id = models.ForeignKey(Building, on_delete=models.CASCADE, verbose_name="building_id",
                                    related_name='blocks', related_query_name='blocks')
    building_game_id = models.CharField(max_length=64, verbose_name="game_model_id")
    floor = models.IntegerField(verbose_name="floor_number")
    elevation = models.DecimalField(max_digits=20, decimal_places=12, blank=True, null=True)
    scale = models.DecimalField(max_digits=20, decimal_places=12, blank=True, null=True)
    rotation = models.DecimalField(max_digits=20, decimal_places=12, blank=True, null=True)


class CharacterModel(models.Model):
    username = models.CharField(max_length=32, db_index=True)
    url = models.CharField(max_length=512)
    thumbnail = models.CharField(max_length=128, blank=True, null=True)


class Parcel(models.Model):
    username = models.CharField(max_length=32, db_index=True)
    name = models.CharField(max_length=128)
    location_x = models.DecimalField(max_digits=20, decimal_places=12, blank=True, null=True)
    location_y = models.DecimalField(max_digits=20, decimal_places=12, blank=True, null=True)
    building_id = models.BigIntegerField(null=True, blank=True)
    thumbnail = models.CharField(max_length=256, blank=True, null=True)


class GlobalGameSetting(models.Model):
    game_full_speed_spinner = models.BooleanField(default=False)
    game_full_boomer = models.BooleanField(default=False)
