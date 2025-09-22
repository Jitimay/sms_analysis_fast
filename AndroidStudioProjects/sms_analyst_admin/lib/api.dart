import 'package:dio/dio.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class Api {
  static final Api I = Api._();
  Api._();

  final Dio dio = Dio(BaseOptions(
    baseUrl: const String.fromEnvironment('API_BASE', defaultValue: 'http://192.168.41.127:5000'),
    connectTimeout: const Duration(seconds: 8),
    receiveTimeout: const Duration(seconds: 12),
    headers: {'Content-Type': 'application/json'},
  ));

  final _storage = const FlutterSecureStorage();

  Future<void> init() async {
    final token = await _storage.read(key: 'jwt');
    if (token != null) {
      dio.options.headers['Authorization'] = 'Bearer $token';
    }
    dio.interceptors.add(InterceptorsWrapper(
      onError: (e, handler) {
        // auto-logout on 401
        if (e.response?.statusCode == 401) {
          _storage.delete(key: 'jwt');
        }
        return handler.next(e);
      },
    ));
  }

  Future<bool> login(String phone, String password) async {
    final res = await dio.post('/auth/login', data: {'phone': phone, 'password': password});
    final token = res.data['access_token'] as String?;
    if (token == null) return false;
    await _storage.write(key: 'jwt', value: token);
    dio.options.headers['Authorization'] = 'Bearer $token';
    return true;
  }

  Future<Map<String, dynamic>> stats() async {
    final res = await dio.get('/admin/stats');
    return Map<String, dynamic>.from(res.data);
    }
  Future<List<dynamic>> users() async {
    final res = await dio.get('/admin/users');
    return (res.data['users'] as List);
  }

  Future<void> logout() async {
    await _storage.delete(key: 'jwt');
    dio.options.headers.remove('Authorization');
  }
}
