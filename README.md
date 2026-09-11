# PowerProtocolGateway Python

这是一个可运行的电力规约转换前置网关，当前提供以下能力：

- 领域资产：site、channel、point、field_device、control_command
- 测点历史：raw_frame、telemetry、device_time、channel_heartbeat、queue_depth，包含质量、来源、校准版本和观测时间
- 可审计动作：map_point、forward_telemetry、preset_control、execute_control、switch_channel，相同幂等键不会重复登记
- 基础流程：frame_processing、mapping_release、remote_control、channel_takeover，支持请求去重和状态推进
- 版本配置：point_map、channel_policy、source_authorization，保留历史版本和当前激活标记

当前版本侧重报文留存、点表版本、动作审计和基础处理流程，高级协调与复杂故障恢复尚未覆盖。

```powershell
python -m powerprotocol --demo
python -m unittest discover -s tests -v
```
