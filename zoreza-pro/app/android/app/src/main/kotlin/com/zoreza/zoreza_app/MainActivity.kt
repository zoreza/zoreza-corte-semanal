package com.zoreza.zoreza_app

import android.content.Intent
import android.os.Build
import android.os.Bundle
import androidx.core.content.FileProvider
import androidx.credentials.CreatePublicKeyCredentialRequest
import androidx.credentials.CredentialManager
import androidx.credentials.GetCredentialRequest
import androidx.credentials.GetPublicKeyCredentialOption
import androidx.credentials.PublicKeyCredential
import io.flutter.embedding.android.FlutterActivity
import io.flutter.embedding.engine.FlutterEngine
import io.flutter.plugin.common.MethodChannel
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import java.io.File

class MainActivity : FlutterActivity() {
    private val INSTALLER_CHANNEL = "com.zoreza.app/installer"
    private val PASSKEY_CHANNEL = "com.zoreza.app/passkeys"

    override fun configureFlutterEngine(flutterEngine: FlutterEngine) {
        super.configureFlutterEngine(flutterEngine)

        // APK installer channel
        MethodChannel(flutterEngine.dartExecutor.binaryMessenger, INSTALLER_CHANNEL)
            .setMethodCallHandler { call, result ->
                if (call.method == "installApk") {
                    val path = call.argument<String>("path")
                    if (path != null) {
                        installApk(path)
                        result.success(true)
                    } else {
                        result.error("INVALID_PATH", "APK path is null", null)
                    }
                } else {
                    result.notImplemented()
                }
            }

        // Passkey / WebAuthn channel
        MethodChannel(flutterEngine.dartExecutor.binaryMessenger, PASSKEY_CHANNEL)
            .setMethodCallHandler { call, result ->
                when (call.method) {
                    "isSupported" -> {
                        result.success(Build.VERSION.SDK_INT >= Build.VERSION_CODES.P)
                    }
                    "createCredential" -> {
                        val options = call.argument<String>("options")
                        if (options == null) {
                            result.error("INVALID_OPTIONS", "Options JSON is null", null)
                            return@setMethodCallHandler
                        }
                        CoroutineScope(Dispatchers.Main).launch {
                            try {
                                val credentialManager = CredentialManager.create(this@MainActivity)
                                val request = CreatePublicKeyCredentialRequest(options)
                                val response = credentialManager.createCredential(
                                    this@MainActivity, request
                                )
                                val credential = response as? androidx.credentials.CreatePublicKeyCredentialResponse
                                if (credential != null) {
                                    result.success(credential.registrationResponseJson)
                                } else {
                                    result.error("CREATE_FAILED", "No se pudo crear la passkey", null)
                                }
                            } catch (e: Exception) {
                                result.error("PASSKEY_ERROR", e.message ?: "Error desconocido", null)
                            }
                        }
                    }
                    "getCredential" -> {
                        val options = call.argument<String>("options")
                        if (options == null) {
                            result.error("INVALID_OPTIONS", "Options JSON is null", null)
                            return@setMethodCallHandler
                        }
                        CoroutineScope(Dispatchers.Main).launch {
                            try {
                                val credentialManager = CredentialManager.create(this@MainActivity)
                                val publicKeyOption = GetPublicKeyCredentialOption(options)
                                val request = GetCredentialRequest(listOf(publicKeyOption))
                                val response = credentialManager.getCredential(
                                    this@MainActivity, request
                                )
                                val credential = response.credential
                                if (credential is PublicKeyCredential) {
                                    result.success(credential.authenticationResponseJson)
                                } else {
                                    result.error("AUTH_FAILED", "No se obtuvo credencial", null)
                                }
                            } catch (e: Exception) {
                                result.error("PASSKEY_ERROR", e.message ?: "Error desconocido", null)
                            }
                        }
                    }
                    else -> result.notImplemented()
                }
            }
    }

    private fun installApk(path: String) {
        val file = File(path)
        val uri = FileProvider.getUriForFile(this, "${applicationInfo.packageName}.fileprovider", file)
        val intent = Intent(Intent.ACTION_VIEW).apply {
            setDataAndType(uri, "application/vnd.android.package-archive")
            addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
            addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        }
        startActivity(intent)
    }
}
