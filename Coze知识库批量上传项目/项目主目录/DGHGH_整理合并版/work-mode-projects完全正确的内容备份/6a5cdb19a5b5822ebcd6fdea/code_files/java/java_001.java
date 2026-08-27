package com.workflow.worker;

import io.camunda.zeebe.client.api.response.ActivatedJob;
import io.camunda.zeebe.client.api.worker.JobClient;
import io.camunda.zeebe.spring.client.annotation.JobWorker;
import io.camunda.zeebe.spring.client.annotation.Variable;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;

import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.TimeUnit;

/**
 * 工作流 Worker 实现
 * 基于 BPMN 流程定义中的 taskDefinition type 自动注册
 */
@Component
public class WorkflowWorker {

    private static final Logger logger = LoggerFactory.getLogger(WorkflowWorker.class);

    /**
     * 验证任务 Worker
     * 对应 Task_Validate
     */
    @JobWorker(type = "validate", timeout = 30000, retries = 3)
    public Map<String, Object> validateData(JobClient client, ActivatedJob job) {
        logger.info("执行验证任务: {}", job.getProcessInstanceKey());

        try {
            // 获取输入变量
            Map<String, Object> variables = job.getVariablesAsMap();
            Object inputData = variables.get("inputData");

            // 业务验证逻辑
            if (inputData == null) {
                throw new IllegalArgumentException("输入数据不能为空");
            }

            // 验证结果
            Map<String, Object> result = new HashMap<>();
            result.put("valid", true);
            result.put("validatedAt", System.currentTimeMillis());

            logger.info("验证任务完成: {}", result);
            return result;

        } catch (Exception e) {
            logger.error("验证任务失败: {}", e.getMessage(), e);
            throw new RuntimeException("验证失败: " + e.getMessage(), e);
        }
    }

    /**
     * 处理任务 Worker
     * 对应 Task_Process
     */
    @JobWorker(type = "process", timeout = 60000, retries = 3)
    public Map<String, Object> processData(JobClient client, ActivatedJob job) {
        logger.info("执行处理任务: {}", job.getProcessInstanceKey());

        try {
            Map<String, Object> variables = job.getVariablesAsMap();

            // 检查前置条件：金额判断
            Double amount = (Double) variables.getOrDefault("amount", 0.0);
            Boolean validationValid = (Boolean) variables.getOrDefault("valid", false);

            if (!validationValid) {
                throw new IllegalStateException("数据验证未通过，无法处理");
            }

            // 业务处理逻辑
            Map<String, Object> result = new HashMap<>();
            result.put("processed", true);
            result.put("amount", amount);
            result.put("processedAt", System.currentTimeMillis());

            // 根据金额决定审批流程
            if (amount <= 10000) {
                result.put("approvalRequired", "manager");
                result.put("nextStep", "manager_approval");
            } else {
                result.put("approvalRequired", "dual");
                result.put("nextStep", "dual_approval");
            }

            logger.info("处理任务完成: {}", result);
            return result;

        } catch (Exception e) {
            logger.error("处理任务失败: {}", e.getMessage(), e);
            throw new RuntimeException("处理失败: " + e.getMessage(), e);
        }
    }

    /**
     * 通知任务 Worker
     * 对应 Task_Notify
     */
    @JobWorker(type = "notify", timeout = 15000, retries = 2)
    public Map<String, Object> sendNotification(JobClient client, ActivatedJob job) {
        logger.info("执行通知任务: {}", job.getProcessInstanceKey());

        try {
            Map<String, Object> variables = job.getVariablesAsMap();
            String notificationType = (String) variables.getOrDefault("notificationType", "email");
            String recipient = (String) variables.get("recipient");

            // 通知逻辑
            Map<String, Object> result = new HashMap<>();
            result.put("notificationSent", true);
            result.put("type", notificationType);
            result.put("recipient", recipient);
            result.put("sentAt", System.currentTimeMillis());

            logger.info("通知任务完成: 已发送 {} 到 {}", notificationType, recipient);
            return result;

        } catch (Exception e) {
            logger.error("通知任务失败: {}", e.getMessage(), e);
            throw new RuntimeException("通知发送失败: " + e.getMessage(), e);
        }
    }

    /**
     * 补偿任务 Worker
     * 对应 Task_Compensate (Saga 补偿)
     */
    @JobWorker(type = "compensate", timeout = 30000, retries = 5)
    public Map<String, Object> compensate(JobClient client, ActivatedJob job) {
        logger.warn("执行补偿任务: {}", job.getProcessInstanceKey());

        try {
            Map<String, Object> variables = job.getVariablesAsMap();

            // 补偿逻辑：回滚已执行的操作
            // 例如：删除已创建记录、退款、撤销审批等

            Map<String, Object> result = new HashMap<>();
            result.put("compensated", true);
            result.put("compensatedAt", System.currentTimeMillis());

            logger.warn("补偿任务完成");
            return result;

        } catch (Exception e) {
            logger.error("补偿任务失败: {}", e.getMessage(), e);
            // 补偿失败需要人工介入
            throw new RuntimeException("补偿失败，需要人工干预: " + e.getMessage(), e);
        }
    }
}