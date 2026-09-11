from __future__ import annotations
from hashlib import sha256
from typing import Any

class ProtocolGateway:
    """Gateway workflows backed by retained frames, versioned configuration and durable jobs."""
    def __init__(self,service:Any)->None:self.service=service
    def keep_frame(self,channel:str,payload:bytes,sequence:int,quality:str="good")->dict:
        sample=self.service.baseline.record_signal(channel,"raw_frame",float(len(payload)),quality=quality,source=f"seq:{sequence}")
        return {"sequence":sequence,"payload_hex":payload.hex(),"sample_sequence":sample.sequence,"quality":quality}
    def map_point(self,point:str,raw:float,mapping:dict)->dict:
        row=mapping[point]; return {"point":point,"engineering_value":raw*float(row.get("scale",1))+float(row.get("offset",0)),"quality":"good"}
    def publish_mapping(self,version:int,mapping:dict,active:bool=True)->dict:return self.service.baseline.publish_config("point_map",version,mapping,active=active)
    def enqueue_fifo(self,site:str,messages:list[dict])->list[dict]:return [dict(m,site=site,queue_order=i) for i,m in enumerate(messages,1)]
    def processing_job(self,request_id:str,channels:list[str],frame_id:str)->dict:return self.service.baseline.create_job("frame_processing",request_id,channels,frame_id=frame_id,steps=["received","mapped","forwarded"])
    def mapping_release_job(self,request_id:str,stations:list[str],version:int)->dict:return self.service.baseline.create_job("mapping_release",request_id,stations,version=int(version),state_model="whole-version")
    def remote_control_job(self,request_id:str,command_asset:str,source:str)->dict:return self.service.baseline.create_job("remote_control",request_id,[command_asset],source=source,phase="requested")
    def source_allowed(self,source:str,station:str,policy:dict)->bool:return source in policy and station in policy[source]
    def assess_channel(self,request_id:str,channel:str,errors:int,frames:int)->dict:
        ratio=int(errors)/max(int(frames),1); verdict="bad" if int(frames)<=0 or ratio>0.05 else "good"
        self.service.baseline.record_signal(channel,"channel_health",ratio,quality=verdict,source="error-ratio")
        return self.service.baseline.create_job("channel_assessment",request_id,[channel],verdict=verdict,error_ratio=ratio)
    def deduplicate_frames(self,request_id:str,channel:str,payloads:list[bytes])->dict:
        seen=set(); kept=[]
        for payload in payloads:
            digest=sha256(payload).hexdigest()
            if digest not in seen: seen.add(digest); kept.append(digest)
        return self.service.baseline.create_job("frame_deduplication",request_id,[channel],kept=kept,basis="payload-hash")
    def publish_retention(self,version:int,record_limit:int)->dict:return self.service.baseline.publish_config("retention_policy",version,{"record_limit":int(record_limit)},active=True)
    def presence_job(self,request_id:str,device:str,heartbeat_age_s:float)->dict:
        state="online" if float(heartbeat_age_s)<=30 else "offline"
        return self.service.baseline.create_job("device_presence",request_id,[device],state=state,heartbeat_age_s=float(heartbeat_age_s))
    def record_point_quality(self,point:str,value:float,quality:str)->dict:return self.service.baseline.record_signal(point,"point_quality",value,quality=quality,source="mapping").__dict__
    def configuration_change(self,request_id:str,site:str,name:str,from_version:int,to_version:int)->dict:return self.service.baseline.create_job("config_change",request_id,[site],name=name,from_version=from_version,to_version=to_version)
    def recall_job(self,request_id:str,station:str,points:list[str])->dict:return self.service.baseline.create_job("station_recall",request_id,[station],points=list(points),mode="full")
